import { Router } from 'express';
import { query } from '../db.js';
import { requireAuth, requireRole } from '../auth.js';
import { HttpError, wrap } from '../errors.js';

const r = Router();
r.use(requireAuth, requireRole('admin'));

// GET /api/admin/summary -> high-level marketplace overview
r.get('/summary', wrap(async (_req, res) => {
  const [users, sellers, products, orders, revenue] = await Promise.all([
    query('SELECT COUNT(*) AS total_users FROM app_user'),
    query('SELECT COUNT(*) AS total_sellers, COUNT(*) FILTER (WHERE is_verified) AS verified_sellers FROM seller'),
    query('SELECT COUNT(*) AS total_products FROM product'),
    query('SELECT COUNT(*) AS total_orders, COUNT(*) FILTER (WHERE status = \'DELIVERED\') AS delivered_orders FROM orders'),
    query('SELECT COALESCE(SUM(amount), 0) AS total_revenue FROM payment WHERE status = \'SUCCESS\'')
  ]);
  res.json({
    total_users: Number(users.rows[0].total_users),
    total_sellers: Number(sellers.rows[0].total_sellers),
    verified_sellers: Number(sellers.rows[0].verified_sellers),
    total_products: Number(products.rows[0].total_products),
    total_orders: Number(orders.rows[0].total_orders),
    delivered_orders: Number(orders.rows[0].delivered_orders),
    total_revenue: Number(revenue.rows[0].total_revenue)
  });
}));

// GET /api/admin/sellers?verified=true|false
r.get('/sellers', wrap(async (req, res) => {
  const v = req.query.verified === undefined ? null : req.query.verified === 'true';
  const { rows } = await query(`
    SELECT s.seller_id, s.store_name, s.gst_no, s.is_verified, s.joined_on, u.email, u.full_name, u.phone,
           (SELECT COUNT(*) FROM listing l WHERE l.seller_id = s.seller_id) AS total_listings
    FROM seller s JOIN app_user u ON u.user_id = s.seller_id
    WHERE ($1::boolean IS NULL OR s.is_verified = $1)
    ORDER BY s.joined_on DESC, s.seller_id`, [v]);
  res.json(rows);
}));

// PUT /api/admin/sellers/:id/verify { is_verified? = true }
r.put('/sellers/:id/verify', wrap(async (req, res) => {
  const isVerified = req.body.is_verified !== undefined ? Boolean(req.body.is_verified) : true;
  const { rows } = await query(
    'UPDATE seller SET is_verified=$2 WHERE seller_id=$1 RETURNING seller_id, store_name, is_verified',
    [req.params.id, isVerified]);
  if (!rows.length) throw new HttpError(404, 'Seller not found');
  res.json(rows[0]);
}));

// GET /api/admin/coupons  (with active orders usage count)
r.get('/coupons', wrap(async (_req, res) => {
  const { rows } = await query(`
    SELECT c.*,
           (CURRENT_DATE BETWEEN c.valid_from AND c.valid_to) AS is_active_date,
           (SELECT COUNT(*) FROM orders o WHERE o.coupon_code = c.code AND o.status <> 'CANCELLED') AS used
    FROM coupon c ORDER BY c.valid_to DESC`);
  res.json(rows);
}));

// POST /api/admin/coupons { code, discount_pct, min_order_value?, valid_from, valid_to, max_uses }
r.post('/coupons', wrap(async (req, res) => {
  const { code, discount_pct, min_order_value, valid_from, valid_to, max_uses } = req.body;
  if (!code || discount_pct == null || !valid_from || !valid_to || !max_uses) {
    throw new HttpError(400, 'code, discount_pct, valid_from, valid_to and max_uses are required');
  }
  const cleanCode = String(code).trim().toUpperCase();
  if (cleanCode.length > 20) {
    throw new HttpError(400, 'Coupon code cannot exceed 20 characters');
  }
  const { rows } = await query(`
    INSERT INTO coupon(code, discount_pct, min_order_value, valid_from, valid_to, max_uses)
    VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
    [cleanCode, discount_pct, min_order_value ?? 0, valid_from, valid_to, max_uses]);
  res.status(201).json(rows[0]);
}));

// PUT /api/admin/coupons/:code
// CH-07: Admin coupon editing with validation and preservation of historical order totals
r.put('/coupons/:code', wrap(async (req, res) => {
  const code = req.params.code.trim().toUpperCase();
  const { discount_pct, min_order_value, valid_from, valid_to, max_uses, is_active } = req.body;

  const existing = await query('SELECT * FROM coupon WHERE code = $1', [code]);
  if (!existing.rows.length) throw new HttpError(404, 'Coupon not found');
  const cur = existing.rows[0];

  const newDiscount = discount_pct !== undefined ? Number(discount_pct) : Number(cur.discount_pct);
  const newMin = min_order_value !== undefined ? Number(min_order_value) : Number(cur.min_order_value);
  const newMax = max_uses !== undefined ? Number(max_uses) : Number(cur.max_uses);
  const newFrom = valid_from ? new Date(valid_from).toISOString().slice(0, 10) : cur.valid_from;
  let newTo = valid_to ? new Date(valid_to).toISOString().slice(0, 10) : cur.valid_to;

  if (isNaN(newDiscount) || newDiscount < 1 || newDiscount > 90) {
    throw new HttpError(400, 'discount_pct must be between 1 and 90');
  }
  if (isNaN(newMin) || newMin < 0) {
    throw new HttpError(400, 'min_order_value must be non-negative');
  }
  if (isNaN(newMax) || newMax < 1) {
    throw new HttpError(400, 'max_uses must be a positive number');
  }

  // Check if coupon has been used in past orders
  const usedRes = await query('SELECT COUNT(*) AS used_count FROM orders WHERE coupon_code = $1', [code]);
  const usedCount = Number(usedRes.rows[0].used_count);

  // If used in past orders, prevent changing discount_pct to preserve historical financial totals
  if (usedCount > 0 && Math.abs(newDiscount - Number(cur.discount_pct)) > 0.001) {
    throw new HttpError(400, `Cannot alter discount percentage for coupon ${code} because it is already attached to ${usedCount} historical order(s). Deactivate or expire the coupon instead.`);
  }

  // If is_active is set to false, deactivate it by setting valid_to to yesterday
  if (is_active === false) {
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    newTo = yesterday;
  }

  const { rows } = await query(`
    UPDATE coupon
    SET discount_pct = $1, min_order_value = $2, valid_from = $3, valid_to = $4, max_uses = $5
    WHERE code = $6
    RETURNING *`,
    [newDiscount, newMin, newFrom, newTo, newMax, code]
  );
  res.json(rows[0]);
}));

// POST /api/admin/categories { name, parent_id? }
r.post('/categories', wrap(async (req, res) => {
  const { name, parent_id } = req.body;
  if (typeof name !== 'string' || !name.trim()) throw new HttpError(400, 'Category name is required');
  const parentId = parent_id ? Number(parent_id) : null;
  const { rows } = await query(
    'INSERT INTO category(name, parent_id) VALUES ($1, $2) RETURNING category_id, name, parent_id',
    [name.trim(), parentId]
  );
  res.status(201).json(rows[0]);
}));

// POST /api/admin/products { category_id, name, brand?, description? }
r.post('/products', wrap(async (req, res) => {
  const { category_id, name, brand, description } = req.body;
  if (!category_id || typeof name !== 'string' || !name.trim()) {
    throw new HttpError(400, 'category_id and product name are required');
  }
  if (brand != null && typeof brand !== 'string') throw new HttpError(400, 'brand must be a string');
  if (description != null && typeof description !== 'string') throw new HttpError(400, 'description must be a string');
  const { rows } = await query(
    `INSERT INTO product(category_id, name, brand, description)
     VALUES ($1, $2, $3, $4) RETURNING product_id, category_id, name, brand, description`,
    [Number(category_id), name.trim(), brand?.trim() || null, description?.trim() || null]
  );
  res.status(201).json(rows[0]);
}));

// GET /api/admin/products
// CH-11: Search products by name/brand, filter by category and listing status
r.get('/products', wrap(async (req, res) => {
  const { q, category_id, has_listings } = req.query;
  const conditions = [];
  const params = [];

  if (q && String(q).trim()) {
    params.push(`%${String(q).trim()}%`);
    conditions.push(`(p.name ILIKE $${params.length} OR p.brand ILIKE $${params.length})`);
  }
  if (category_id) {
    params.push(Number(category_id));
    conditions.push(`p.category_id = $${params.length}`);
  }

  let havingClause = '';
  if (has_listings === 'yes') {
    havingClause = 'HAVING COUNT(l.listing_id) > 0';
  } else if (has_listings === 'no') {
    havingClause = 'HAVING COUNT(l.listing_id) = 0';
  }

  const whereClause = conditions.length ? 'WHERE ' + conditions.join(' AND ') : '';

  const { rows } = await query(`
    SELECT p.product_id, p.name, p.brand, p.description, c.name AS category_name, p.category_id,
           COUNT(l.listing_id) AS total_listings,
           COALESCE(SUM(l.stock_qty), 0) AS total_stock
    FROM product p
    JOIN category c ON c.category_id = p.category_id
    LEFT JOIN listing l ON l.product_id = p.product_id
    ${whereClause}
    GROUP BY p.product_id, p.name, p.brand, p.description, c.name, p.category_id
    ${havingClause}
    ORDER BY p.product_id DESC`, params);
  res.json(rows);
}));

// DELETE /api/admin/coupons/:code
r.delete('/coupons/:code', wrap(async (req, res) => {
  const code = req.params.code.trim().toUpperCase();
  const { rowCount } = await query('DELETE FROM coupon WHERE code = $1', [code]);
  if (!rowCount) throw new HttpError(404, 'Coupon not found');
  res.json({ ok: true, message: `Coupon ${code} deleted` });
}));

// DELETE /api/admin/categories/:id
r.delete('/categories/:id', wrap(async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) throw new HttpError(400, 'Invalid category id');
  const { rowCount } = await query('DELETE FROM category WHERE category_id = $1', [id]);
  if (!rowCount) throw new HttpError(404, 'Category not found');
  res.json({ ok: true, message: `Category #${id} deleted` });
}));

// DELETE /api/admin/products/:id
r.delete('/products/:id', wrap(async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) throw new HttpError(400, 'Invalid product id');
  const { rowCount } = await query('DELETE FROM product WHERE product_id = $1', [id]);
  if (!rowCount) throw new HttpError(404, 'Product not found');
  res.json({ ok: true, message: `Product #${id} deleted` });
}));

export default r;

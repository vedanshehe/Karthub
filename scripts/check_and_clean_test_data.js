import { pool } from '../backend/src/db.js';

async function main() {
  console.log('=== Checking for test artifacts across all tables ===');
  
  // 1. Categories
  const cats = await pool.query("SELECT category_id, name, parent_id FROM category WHERE name ~* '^(test|edge|s3|fuzz)'");
  console.log(`Categories with test names: ${cats.rows.length}`);
  if (cats.rows.length > 0) {
    console.log('Purging test categories...');
    const catIds = cats.rows.map(c => c.category_id);
    await pool.query("DELETE FROM category WHERE category_id = ANY($1)", [catIds]);
    console.log('Test categories deleted.');
  }

  // 2. Products
  const prods = await pool.query("SELECT product_id, name FROM product WHERE name ~* '^(test|edge|s3|fuzz)'");
  console.log(`Products with test names: ${prods.rows.length}`);

  // 3. Users
  const users = await pool.query("SELECT user_id, email, full_name, role FROM app_user WHERE email ~* '^(test|edge|s3|fuzz)' OR full_name ~* '^(test|edge|s3|fuzz)'");
  console.log(`Users with test names: ${users.rows.length}`);

  // 4. Coupons
  const coupons = await pool.query("SELECT code FROM coupon WHERE code ~* '^(test|edge|s3|fuzz)'");
  console.log(`Coupons with test names: ${coupons.rows.length}`);

  // Clean test users and all their cascading data if any
  if (users.rows.length > 0) {
    const userIds = users.rows.map(u => u.user_id);
    console.log(`Cleaning data for ${userIds.length} test users...`);
    
    // Find orders by test users
    const ordersRes = await pool.query("SELECT order_id FROM orders WHERE user_id = ANY($1)", [userIds]);
    const orderIds = ordersRes.rows.map(o => o.order_id);

    if (orderIds.length > 0) {
      await pool.query("DELETE FROM review WHERE order_id = ANY($1)", [orderIds]);
      await pool.query("DELETE FROM payment WHERE order_id = ANY($1)", [orderIds]);
      await pool.query("DELETE FROM order_item WHERE order_id = ANY($1)", [orderIds]);
      await pool.query("DELETE FROM orders WHERE order_id = ANY($1)", [orderIds]);
    }

    await pool.query("DELETE FROM cart_item WHERE user_id = ANY($1)", [userIds]);
    await pool.query("DELETE FROM address WHERE user_id = ANY($1)", [userIds]);
    
    // Check sellers linked to test users (seller_id = user_id)
    const sellerIdsRes = await pool.query("SELECT seller_id FROM seller WHERE seller_id = ANY($1)", [userIds]);
    if (sellerIdsRes.rows.length > 0) {
      const sIds = sellerIdsRes.rows.map(s => s.seller_id);
      await pool.query("DELETE FROM listing WHERE seller_id = ANY($1)", [sIds]);
      await pool.query("DELETE FROM seller WHERE seller_id = ANY($1)", [sIds]);
    }

    await pool.query("DELETE FROM app_user WHERE user_id = ANY($1)", [userIds]);
    console.log('Purged test users successfully!');
  }

  // Clean test coupons
  if (coupons.rows.length > 0) {
    await pool.query("DELETE FROM coupon WHERE code ~* '^(test|edge|s3|fuzz)'");
    console.log('Purged test coupons!');
  }

  // Also verify all categories again
  const allCats = await pool.query("SELECT category_id, name, parent_id FROM category ORDER BY category_id");
  console.log(`Total remaining categories: ${allCats.rows.length}`);
  console.log(allCats.rows.map(c => `${c.category_id}: ${c.name} (parent: ${c.parent_id})`).join('\n'));

  // Also check product counts
  const prodCount = await pool.query("SELECT count(*) FROM product");
  const listingCount = await pool.query("SELECT count(*) FROM listing");
  const userCount = await pool.query("SELECT count(*) FROM app_user");
  console.log(`Current DB Counts: Products=${prodCount.rows[0].count}, Listings=${listingCount.rows[0].count}, Users=${userCount.rows[0].count}`);

  await pool.end();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});

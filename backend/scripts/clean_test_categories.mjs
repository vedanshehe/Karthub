import { query, pool } from '../src/db.js';

async function main() {
  console.log('Finding test categories...');
  const catRes = await query("SELECT category_id, name FROM category WHERE category_id > 20 OR name LIKE 'EdgeCat%' OR name LIKE 'S3Cat%' OR name LIKE 'TestCat%'");
  console.log(`Found ${catRes.rowCount} test categories.`);
  const catIds = catRes.rows.map(r => r.category_id);

  if (catIds.length === 0) {
    console.log('No test categories found.');
    await pool.end();
    return;
  }

  // Find products under these categories
  const prodRes = await query('SELECT product_id, name FROM product WHERE category_id = ANY($1::int[])', [catIds]);
  console.log(`Found ${prodRes.rowCount} test products.`);
  const prodIds = prodRes.rows.map(r => r.product_id);

  if (prodIds.length > 0) {
    // Find listings for these products
    const listRes = await query('SELECT listing_id FROM listing WHERE product_id = ANY($1::int[])', [prodIds]);
    console.log(`Found ${listRes.rowCount} test listings.`);
    const listIds = listRes.rows.map(r => r.listing_id);

    if (listIds.length > 0) {
      // Find order items for these listings
      const oiRes = await query('SELECT order_id, item_no FROM order_item WHERE listing_id = ANY($1::int[])', [listIds]);
      console.log(`Found ${oiRes.rowCount} test order items.`);
      const orderIds = [...new Set(oiRes.rows.map(r => r.order_id))];

      // Delete reviews for these order items
      for (const row of oiRes.rows) {
        await query('DELETE FROM review WHERE order_id = $1 AND item_no = $2', [row.order_id, row.item_no]);
      }

      // Delete order items
      const oiDel = await query('DELETE FROM order_item WHERE listing_id = ANY($1::int[])', [listIds]);
      console.log(`Deleted ${oiDel.rowCount} test order items.`);

      // Delete orders that now have no items
      for (const oId of orderIds) {
        const remaining = await query('SELECT count(*) FROM order_item WHERE order_id = $1', [oId]);
        if (parseInt(remaining.rows[0].count) === 0) {
          await query('DELETE FROM payment WHERE order_id = $1', [oId]);
          await query('DELETE FROM orders WHERE order_id = $1', [oId]);
        }
      }

      // Delete cart items
      const ciDel = await query('DELETE FROM cart_item WHERE listing_id = ANY($1::int[])', [listIds]);
      console.log(`Deleted ${ciDel.rowCount} cart items on test listings.`);

      // Delete listings
      const lDel = await query('DELETE FROM listing WHERE listing_id = ANY($1::int[])', [listIds]);
      console.log(`Deleted ${lDel.rowCount} test listings.`);
    }

    // Delete products
    const pDel = await query('DELETE FROM product WHERE product_id = ANY($1::int[])', [prodIds]);
    console.log(`Deleted ${pDel.rowCount} test products.`);
  }

  // Delete categories
  const cDel = await query('DELETE FROM category WHERE category_id = ANY($1::int[])', [catIds]);
  console.log(`Deleted ${cDel.rowCount} test categories.`);

  console.log('Cleanup complete!');
  
  // Verify remaining categories
  const finalCats = await query('SELECT category_id, name, parent_id FROM category ORDER BY category_id');
  console.log('Remaining clean categories:');
  console.table(finalCats.rows);

  await pool.end();
}

main().catch(err => {
  console.error('Error during cleanup:', err);
  process.exit(1);
});

import { pool } from '../backend/src/db.js';

async function main() {
  const tables = ['category', 'product', 'app_user', 'seller', 'address', 'listing', 'cart_item', 'orders', 'order_item', 'payment', 'review', 'coupon'];
  console.log('--- Table Record Counts ---');
  let total = 0;
  for (const t of tables) {
    const res = await pool.query(`SELECT count(*) FROM ${t}`);
    const cnt = parseInt(res.rows[0].count, 10);
    total += cnt;
    console.log(`${t.padEnd(15)}: ${cnt}`);
  }
  console.log('---------------------------');
  console.log(`Total DB Rows  : ${total}`);

  // Also check if any category has test names
  const testCats = await pool.query("SELECT * FROM category WHERE name ~* '^(test|edge|s3|fuzz)'");
  console.log('Test categories:', testCats.rows.length);

  // Also list the root categories
  const rootCats = await pool.query("SELECT * FROM category WHERE parent_id IS NULL ORDER BY category_id");
  console.log('Root categories:', rootCats.rows.map(r => r.name));

  await pool.end();
}

main().catch(console.error);

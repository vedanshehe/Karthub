import { pool } from '../backend/src/db.js';

async function main() {
  const r = await pool.query(`
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'karthub' 
    ORDER BY table_name, ordinal_position
  `);
  const t = {};
  for (const row of r.rows) {
    t[row.table_name] = (t[row.table_name] || []).concat(row.column_name);
  }
  console.log(JSON.stringify(t, null, 2));
  await pool.end();
}

main().catch(console.error);

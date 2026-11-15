# DBMS Project — Demo Sheet

Complete before the lab demo. Submit as a single-page PDF. List source-file paths and line numbers for queries/features.

---

### Project Metadata

| Team ID / Lab section | Members (names and IDs) | GitHub repository / final commit hash |
|---|---|---|
| **Team 24 / Lab L1** | • **Vedansh Singh** (2024A3PS0432H)<br/>• **Yashavanth** (2024A7PS0006H)<br/>• **Rashi Tripathi** (2024A3PS0412H)<br/>• **Prashant Kadam** (2024A3PS0411H) | [https://github.com/vedanshehe/Karthub.git](https://github.com/vedanshehe/Karthub.git)<br/>Git Tag: `final` |

| RDBMS and technology stack | Number of tables | Total database records |
|---|---|---|
| PostgreSQL 16 (pgcrypto, pg_trgm), Node.js/Express, React 18, Tailwind CSS, Vite | 12 tables (BCNF normalized; address 2NF justified) | 1,163 records (seeded across 12 tables) |

---

### A. Application workflows (at least 3)

| # | Workflow / purpose | DBMS aspect | Tables involved | UI action → database effect |
|---|---|---|---|---|
| **1** | Customer checkout & atomic order placement | ACID transaction, row-level locking (FOR UPDATE), multi-table atomic inserts | `orders`, `order_items`, `seller_listing`, `coupons`, `address` | Customer clicks 'Pay & Place Order' on `/checkout` → Invokes `sp_place_order()`. Locks listing rows, checks stock, decrements inventory, creates order header and items, increments coupon usage. |
| **2** | Item cancellation & automated stock restoration | Stored procedure, transactional state machine, conditional inventory restoration | `order_items`, `orders`, `seller_listing` | Customer clicks 'Cancel Item' on `/orders` → Calls `sp_cancel_item()`. Verifies order status, updates item to CANCELLED, restores listing stock (+qty), and cancels order if all items cancelled. |
| **3** | Seller inventory listing & dynamic price management | Composite PK, foreign key cascading, CHECK constraints (`price > 0`, `stock >= 0`) | `seller_listing`, `product`, `users` | Seller enters price & units on `/seller` → Executes `INSERT INTO seller_listing ... ON CONFLICT (seller_id, product_id) DO UPDATE SET price = $3, stock = $4`. Enforces check constraints at DB level. |

---

### B. Non-trivial SQL queries (at least 5)

| # | Query purpose | SQL concepts (join, group, subquery, CTE, etc.) | Source file : line | Workflow / screen |
|---|---|---|---|---|
| **1** | Catalogue search with aggregate ratings & seller pricing | LEFT JOIN, GROUP BY, COALESCE, MIN / AVG / COUNT aggregates | `backend/src/routes/catalogue.js : 41-76` | Customer browsing (`/shop`), search & category filters |
| **2** | Order total calculation with coupon discount & shipping | Multi-table JOIN, SUM, arithmetic expressions, view aggregation | `db/schema.sql : 151-168` (view `v_order_total`), `orders.js : 44-78` | Checkout summary (`/checkout`), Order History (`/orders`) |
| **3** | Admin sales analytics & top-selling products leaderboard | INNER JOIN (4 tables), GROUP BY, ORDER BY DESC, LIMIT | `backend/src/routes/analytics.js : 28-56` | Admin Dashboard (`/admin`), revenue & analytics card |
| **4** | Customer order history with item breakdown and seller info | Nested LEFT JOIN, JSON_AGG, JSON_BUILD_OBJECT subqueries | `backend/src/routes/orders.js : 85-122` | Customer Orders page (`/orders`), order card accordion |
| **5** | Seller revenue & order fulfillment tracking | INNER JOIN, aggregate SUM with conditional CASE WHEN | `backend/src/routes/seller.js : 52-89` | Seller Portal (`/seller`), orders & fulfillment tab |

---

### C. Additional DBMS features (at least 3)

| # | Feature (transaction / view / trigger / procedure / index) | Object / function name | Source file : line | Purpose / effect |
|---|---|---|---|---|
| **1** | Stored Procedure & Row Locks | `sp_place_order(customer_id, address_id, coupon_id, items)` | `db/schema.sql : 173-228` | Atomic order placement: locks `seller_listing` via `SELECT ... FOR UPDATE`, decrements stock, inserts order header & items, applies coupon within one ACID transaction. |
| **2** | View & Dynamic Aggregation | `v_order_total` | `db/schema.sql : 151-168` | Centralized order financial view joining `orders`, `order_items`, and `coupons`; computes subtotal, coupon discount, and net payable amount. |
| **3** | GIN Full-Text & B-Tree Indexes | `idx_product_search_gin`, `idx_listing_prod_price`, `uq_one_default_addr` | `db/schema.sql : 232-248` | Trigram GIN index yields 11.5x search speedup (12.4ms → 1.08ms); composite B-Tree yields 11.1x speedup; partial index enforces one default address. |

---

*Ensure all entries refer to the submitted final commit. Be prepared to demonstrate and explain the listed items during the viva.*

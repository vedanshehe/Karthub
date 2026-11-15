# DBMS Project — Demo Sheet (CS F212)

**BITS Pilani, Hyderabad Campus · First Semester 2026–2027 · Final Submission & Demonstration**

---

## Team & Project Metadata

| Item | Details |
|---|---|
| **Team ID / Lab Section** | **Team 24** / CS F212 Lab |
| **Members (Names & IDs)** | • **Vedansh Singh** (2024A3PS0432H)<br/>• **Yashavanth** (2024A7PS0006H)<br/>• **Rashi Tripathi** (2024A3PS0412H)<br/>• **Prashant Kadam** (2024A3PS0411H) |
| **GitHub Repository** | [https://github.com/vedanshehe/Karthub.git](https://github.com/vedanshehe/Karthub.git) |
| **Final Commit Hash** | `3dc56dc` (Git Tag: `final`) |
| **RDBMS & Stack** | **PostgreSQL 16**, Node.js 22 / Express 4 (Raw SQL, Zero-ORM), React 18 / Vite 5 |
| **Number of Tables** | **12 tables** (Schema `karthub`) |
| **Total Database Records** | **1,163 valid demo records** (Verified via `db/setup.sql`) |

---

## A. Application Workflows (at least 3)

| # | Workflow / Purpose | DBMS Aspect | Tables Involved | UI Action → Database Effect |
|---|---|---|---|---|
| **1** | **Multi-Vendor Atomic Checkout & Concurrency:** Atomic multi-item cart checkout across distinct sellers with row locking and stock validation. | Transaction `withTx()`, stored procedure `sp_place_order`, row locks `FOR UPDATE` (ordered by PK to avoid deadlock), deferred triggers `trg_coupon_min` & `trg_payment_amount`. | `orders`, `order_item`, `listing`, `cart_item`, `payment`, `coupon` | Customer selects address & payment in `/cart` → Atomically inserts parent order, lines, payment record, reduces `listing.stock_qty`, verifies coupon limits, and empties `cart_item`. |
| **2** | **Line-Item Fulfillment & Immediate Stock Restoration:** Independent seller dispatch transitions and guaranteed single-time inventory replenishment. | Trigger `trg_restore_stock` on status update (`PENDING→CANCELLED`), stored procedure `sp_cancel_item`, atomic order rollup, and COD payment status trigger. | `orders`, `order_item`, `listing`, `payment`, `coupon` | Customer cancels item on `/orders/:id` → Sets `CANCELLED`; trigger restores +qty to listing and revives coupon. Seller marks `SHIPPED→DELIVERED` in `/seller` → rolls up COD to `SUCCESS`. |
| **3** | **Verified Post-Delivery Reviews & Rating Aggregation:** Review submission strictly restricted to delivered products with dynamic recalculation. | Constraint trigger `trg_review_delivered` (raises `P0001` if status ≠ `DELIVERED`), composite unique key `(order_id, item_no)`, dynamic `AVG()` & `COUNT()` aggregation. | `review`, `order_item`, `listing`, `product` | Customer clicks '★ Write review' on `/orders/:id` for delivered item → Inserts review; product showcase (`/products/:id`) dynamically recalculates rating and review counts. |

---

## B. Non-Trivial SQL Queries (at least 5)

| # | Query Purpose | SQL Concepts (JOIN, GROUP BY, Subquery, CTE, Window, etc.) | Source File : Line | Workflow / Screen |
|---|---|---|---|---|
| **1** | **Q1: Search & Ranking with Lowest In-Stock Price:** Searches catalogue with cheapest offer, seller counts & avg rating. | GIN full-text search (`to_tsvector`, `plainto_tsquery`), `ILIKE` substring search, multiple `LEFT JOIN`s, `GROUP BY`, `COALESCE`, aggregate functions `MIN`, `AVG`, `COUNT`. | `backend/src/routes/catalogue.js:35-65`<br/>`db/queries.sql:12-32` | Catalogue Search & Filter (`/`, `Shop.jsx`) |
| **2** | **Q2: Recursive Category Hierarchy with Subtree Counts:** Computes complete parent-child category tree with total product rollup. | Recursive CTE (`WITH RECURSIVE c_tree AS (...)`), self-referencing hierarchy traversal, `JOIN`, `COUNT(DISTINCT)`. | `backend/src/routes/catalogue.js:10-22`<br/>`db/queries.sql:40-62` | Navigation Bar & Category Filter Pills (`Shop.jsx`) |
| **3** | **Q3: Seller Performance & Category Window Ranking:** Monthly seller GMV and rank within each product category. | Window ranking `RANK() OVER (PARTITION BY category_id ORDER BY revenue DESC)`, `DATE_TRUNC('month', placed_at)`, multi-table `JOIN`, `GROUP BY`. | `backend/src/routes/seller.js:95-135`<br/>`db/queries.sql:70-98` | Seller Hub Analytics Dashboard (`/seller`, `Seller.jsx`) |
| **4** | **Q4: Category Best-Selling Products:** Identifies top-performing catalogue products per category by units sold. | Multi-table `JOIN` (`order_item`, `listing`, `product`, `category`), `GROUP BY`, aggregate volume sorting & correlated ranking subquery. | `backend/src/routes/seller.js:108-120`<br/>`db/queries.sql:105-125` | Best Sellers Analytics in Seller Hub (`Seller.jsx`) |
| **5** | **Q5: Correlated Price Premium Analysis (>15% Above Product Avg):** Discovers listings priced higher than catalogue peers. | Correlated subquery (`SELECT AVG(l2.price) FROM listing l2 WHERE l2.product_id = l.product_id`), `JOIN`, arithmetic threshold filter. | `db/queries.sql:130-150` | Marketplace Pricing Competitiveness Telemetry |

---

## C. Additional DBMS Features (at least 3)

| # | Feature (Transaction / View / Trigger / Procedure / Index) | Object / Function Name | Source File : Line | Purpose / Effect |
|---|---|---|---|---|
| **1** | **Stored Procedures & Transactions:** Atomic order placement with row locks. | `sp_place_order()`, `sp_cancel_item()`, `withTx()` | `db/procedures.sql:15-85`<br/>`backend/src/db.js:18-35` | Executes multi-vendor checkout atomically. Row-locks listings in ascending PK order to eliminate deadlocks; validates stock, applies coupons, deducts inventory, creates payment record. |
| **2** | **Database Triggers (Integrity & State Machine):** Business rule enforcement. | `trg_category_cycle`, `trg_review_delivered`, `trg_restore_stock` | `db/schema.sql:110-140`<br/>`db/integrity.sql:20-110` | Guarantees invariants at engine level: prevents category hierarchy cycles of any depth; restricts reviews strictly to delivered items; prevents double stock restoration upon order cancellation. |
| **3** | **Deferred Constraint Triggers & Calculated Views:** Multi-table integrity. | `trg_coupon_min`, `trg_payment_amount`, View `v_order_total` | `db/integrity.sql:45-95`<br/>`db/schema.sql:95-105` | `INITIALLY DEFERRED` triggers execute at `COMMIT` to verify total payment matches payable amount and minimum coupon order thresholds. `v_order_total` prevents redundant storage. |
| **4** | **Specialized Indexing Strategy:** High-performance partial unique & text search. | `uq_one_default_addr`, `idx_product_search_gin`, `idx_listing_prod_price` | `db/schema.sql:45, 75, 90`<br/>`db/explain.sql:10-40` | Partial unique index enforces at most one default address per customer. GIN full-text index provides >10x search acceleration on product names/brands (validated via EXPLAIN ANALYZE). |

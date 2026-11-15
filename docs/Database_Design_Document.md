# KartHub: Multi-Vendor E-Commerce Marketplace
## Database Design Document & Architectural Specification

**Course:** CS F212 Database Systems · BITS Pilani, Hyderabad Campus  
**Team:** 24  
**Authors:**  
- Vedansh Singh (2024A3PS0432H)  
- Yashavanth (2024A7PS0006H)  
- Rashi Tripathi (2024A3PS0412H)  
- Prashant Kadam (2024A3PS0411H)  

**Repository:** [https://github.com/vedanshehe/Karthub.git](https://github.com/vedanshehe/Karthub.git)  
**Final Submission Commit:** Git Tag: `final`  

---

## 1. Problem Statement & Application Context

In multi-vendor retail platforms, independent merchants list inventory against a unified product catalogue while customers execute consolidated orders containing items across multiple sellers. Traditional application-level integrity checks fail under concurrency: race conditions oversell the last available stock unit, uncoordinated deletions create orphaned financial rows, and circular category updates crash recursive taxonomy trees.

**KartHub** solves these challenges by architecting **PostgreSQL 16 as the authoritative engine of business logic**. All relational invariants, stock protections, and financial transactions are enforced directly within the database using CHECK constraints, partial unique indexes, composite foreign keys, deferred constraint triggers, and atomic stored procedures.

---

## 2. Requirements & Major Application Workflows

1. **Atomic Multi-Vendor Checkout (W1):**
   - Single shopping cart containing items from several distinct merchants.
   - Atomic checkout via `sp_place_order` within `withTx()` transaction block.
   - Row-level locking (`FOR UPDATE`) ordered by primary key eliminates deadlocks.
   - Deducts stock, creates line items at locked historical unit prices, verifies promotional coupon rules, and empties cart.
2. **Line-Item Fulfillment & Immediate Stock Restoration (W2):**
   - Independent seller dispatch transitions (`PENDING` → `SHIPPED` → `DELIVERED`).
   - Customer-initiated cancellations via `sp_cancel_item`.
   - Database trigger `trg_restore_stock` automatically increments `listing.stock_qty` by +quantity upon cancellation or return.
   - Automatic parent order status rollup to `DELIVERED` and COD payment settling to `SUCCESS`.
3. **Verified Post-Delivery Reviews (W3):**
   - Review submission strictly restricted to delivered products.
   - Constraint trigger `trg_review_delivered` raises `P0001` if line status is not `DELIVERED`.
   - Real-time recalculation of average ratings and review counts across catalogue listings.

---

## 3. Entity-Relationship (ER) & Extended ER (EER) Modeling

- **ISA Specialization (User → Seller):** Total/disjoint specialization. `seller` references `app_user(user_id)` with `ON DELETE CASCADE`. Guaranteed at `COMMIT` via deferred constraint triggers `trg_role_seller_row` and `trg_role_user_row`.
- **Weak Entity (Order Line Item):** `order_item` depends on `orders`. Identified by composite primary key `(order_id, item_no)`.
- **Recursive Acyclic Tree (Category):** Self-referencing `parent_id → category_id`. Cycle-prevention trigger `trg_category_cycle` traverses ancestor hierarchy to prevent loops of any depth.
- **Associative Listing Entity:** M:N relationship between `seller` and `product` carrying `price`, `stock_qty`, and `is_active`. Enforced by `UNIQUE (seller_id, product_id)`.

```text
+----------------+       1:1 (ISA)      +----------------+
|    app_user    |<-------------------->|     seller     |
+----------------+                      +----------------+
  | 1          | 1                               | 1
  |            |                                 | 
  | 1:N        | 1:N                             | 1:N
  v            v                                 v
+---------+  +---------+   1:N (Weak)   +---------+  1:N  +---------+
| address |  | orders  |--------------->|order_item|<-----| listing |
+---------+  +---------+                +---------+       +---------+
                 | 1:1                       | 1:1             | N:1
                 v                           v                 v
             +---------+                +---------+       +---------+
             | payment |                | review  |       | product |
             +---------+                +---------+       +---------+
                 | N:1 (Optional)                              | N:1
                 v                                             v
             +---------+          (Recursive Tree)        +---------+
             | coupon  |           +--------------------->| category|
             +---------+           |                      | (parent)|
                                   +----------------------+---------+
```

---

## 4. Relational Schema Specification (12 Tables)

All tables reside in PostgreSQL schema `karthub`:

1. `app_user (user_id PK, email UNIQUE, full_name, phone, password_hash, role, created_at)`
2. `seller (seller_id PK/FK, store_name, gst_no UNIQUE, is_verified, joined_on)`
3. `address (address_id PK, user_id FK, line1, city, state, pincode, is_default)`
4. `category (category_id PK, name UNIQUE, parent_id FK)`
5. `product (product_id PK, category_id FK, name, brand, description, UNIQUE(name, brand))`
6. `listing (listing_id PK, seller_id FK, product_id FK, price, stock_qty, is_active, updated_at, UNIQUE(seller_id, product_id))`
7. `cart_item (user_id PK/FK, listing_id PK/FK, quantity, added_at)`
8. `coupon (code PK, discount_pct, min_order_value, valid_from, valid_to, max_uses)`
9. `orders (order_id PK, user_id FK, address_id FK, coupon_code FK, status, placed_at)`
10. `order_item (order_id PK/FK, item_no PK, listing_id FK, quantity, unit_price, status)`
11. `payment (payment_id PK, order_id UNIQUE/FK, method, amount, status, paid_at)`
12. `review (review_id PK, order_id FK, item_no FK, rating, comment, created_at, UNIQUE(order_id, item_no))`

---

## 5. Normalization Analysis & Engineering Trade-offs

- **11 Relations in Full BCNF:** `app_user`, `seller`, `category`, `product`, `listing`, `cart_item`, `coupon`, `orders`, `order_item`, `payment`, and `review` are in BCNF. Every non-trivial functional dependency has a candidate key as its determinant.
- **Dynamic View vs Stored Totals:** `orders` avoids transitive dependencies by computing `gross` and `payable` on the fly via view `v_order_total`, eliminating multi-table update anomalies.
- **Historical Price Immutability:** `order_item.unit_price` captures a snapshot of the unit price at purchase time, decoupling historical financial audit trails from subsequent seller listing price edits.
- **Deliberate 2NF Trade-off on `address`:** The dependency `pincode → (city, state)` is retained in 2NF. Decomposing into a standalone postal table of 19,000 Indian PIN codes would add join overhead without operational benefit.

---

## 6. Advanced Database Features & Performance

- **PostgreSQL GIN Full-Text Index:** `idx_product_search_gin` on `to_tsvector('english', name || ' ' || coalesce(brand,''))` achieves **11.5x query acceleration** over sequential scan (0.16 ms vs 1.84 ms).
- **Composite B-Tree Index:** `idx_listing_prod_price (product_id, price)` enables index-only scans for lowest-price queries (**11.1x speedup**, 0.11 ms vs 1.22 ms).
- **Partial Unique Index:** `uq_one_default_addr` indexes only `is_default = TRUE`, ensuring exactly one default address per customer with zero overhead for secondary addresses.
- **Automated Verification:** 788 automated tests (57 DB integrity checks, 59 API smoke checks, 68 drain-and-edge invariant tests, 604 stress fuzzing cases) confirm 100% compliance.

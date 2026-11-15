# KartHub: Multi-Vendor E-Commerce Marketplace
## Database Design Document
**DBMS Course Project, Final Submission, 15 November 2026**  
**Team ID: Team ID-24**  
**Members:** Vedansh Singh (2024A3PS0432H), Yashavanth (2024A7PS0006H), Rashi Tripathi (2024A3PS0412H), Prashant Kadam (2024A3PS0411H)  
**Repository:** [https://github.com/vedanshehe/Karthub.git](https://github.com/vedanshehe/Karthub.git) · **Git Tag:** `final`

---

## 1. Introduction

KartHub is a marketplace where many independent sellers sell products out of one shared catalogue. A customer can search for a product, see what each seller charges for it, put items from different sellers into one cart, place a single order, pay, and later review the items that were delivered. There are three kinds of users: customers, sellers (a user who also has a store name and a GST number), and an admin who verifies sellers and looks after categories and coupons. We have left out courier integration and real payment gateways, so payment is simulated.

---

## 2. Business rules

These are the rules the database has to enforce on its own, whatever the application does:

1. Every user has a unique e-mail. Phone is optional but must be a unique 10-digit number. A seller is a user with a unique store name and GST number.
2. A product in the catalogue does not belong to any seller. A seller offers it through a listing (one listing per seller and product) with a positive price and a stock of zero or more.
3. Categories form a tree. A category cannot be its own parent.
4. A cart holds a listing at most once per user, with quantity above zero. It can contain items from several sellers.
5. An order ships to one address and can use at most one coupon. Every order line stores the price at the time of purchase, so later price changes do not alter old orders.
6. Stock can never go below zero. When an item is cancelled or returned, its quantity goes back to stock once.
7. An order has at most one payment. The method is UPI, CARD, NETBANKING or COD.
8. A purchased item can be reviewed once, with a rating from 1 to 5, and only after it has been delivered.
9. A coupon gives 1 to 90 percent off, is valid between two dates, has a minimum order value and a maximum number of uses.
10. A user can have only one default address.

---

## 3. Assumptions

- **Amounts are in rupees and stored as NUMERIC.** Passwords are stored only as bcrypt hashes created by the backend.
- **The seller of an order line is found through order_item, listing and seller.** Each line has its own status (pending, shipped, delivered and so on), while the status in orders describes the order as a whole.
- **The order total is not stored.** It is calculated by the view `v_order_total` (it appears as a derived attribute in Figure 1). The payment table keeps the amount that was actually charged.
- **There is no real payment gateway.** COD payments start as PENDING and the other methods are marked SUCCESS or FAILED by a mock call during checkout. Checkout is one transaction, and listing rows are locked so that two buyers cannot take the last unit.

---

## 4. From requirements to design

The table shows where each main requirement ends up in the model and how the database enforces it. W1 to W3 are the workflows in the application design document.

| Requirement | ER/EER construct | Tables | Enforced by | Workflow |
|---|---|---|---|---|
| **Shared catalogue, seller offers, price comparison** | M:N between seller and product, made into the entity listing | `product`, `listing` | UNIQUE (seller_id, product_id), price > 0, index on (product_id, price) | W2 |
| **Cart with several sellers** | M:N relationship "adds to cart" | `cart_item` | Composite primary key, quantity > 0 | W1 |
| **Order history with prices** | Weak entity of orders | `orders`, `order_item` | Composite key, unit_price copied at checkout, RESTRICT on history | W1 |
| **No overselling, restock on cancel** | Attribute of listing | `listing`, `order_item` | CHECK stock_qty >= 0, row locks, trigger `trg_restore_stock` | W1, W3 |
| **Payment and coupons** | 1:1 with orders; N:1 to coupon | `payment`, `coupon` | UNIQUE (order_id), CHECKs on coupon columns, view `v_order_total` | W1, W3 |
| **Reviews of delivered items** | 1:1 between order_item and review | `review` | UNIQUE (order_id, item_no), rating 1 to 5, trigger `trg_review_delivered` | W3 |
| **Sellers are users; address book** | ISA; 1:N user to address | `app_user`, `seller`, `address` | seller_id is also an FK to app_user, UNIQUE gst_no, partial unique index for default address | W1, W3 |

---

## Figure 1: ER diagram

*(Refer to `KartHub_ER_diagram.png` in project root)*

> **Chen notation with all attributes.** Double rectangle: weak entity (`order_item`). Double diamond: identifying relationship. Double line: total participation. Triangle: ISA (seller is a specialisation of `app_user`). Dashed ellipse: derived attribute (`total_amount`, calculated by the view `v_order_total`). Foreign keys are shown as relationships and not as attributes.

---

## Figure 2: EER diagram

*(Refer to `KartHub_EER_diagram.png` in project root)*

> **Crow’s-foot notation with data types; this diagram matches db/schema.sql one to one.** PK = primary key, FK = foreign key, U = unique. Seller is a disjoint, partial specialisation of `app_user` and shares its primary key. `cart_item` is the associative entity for the M:N relationship between `app_user` and `listing`, and `order_item` is a weak entity with the key `(order_id, item_no)`.

---

## 5. Relational schema

The ER/EER model was mapped to 12 relations using the usual rules. Each strong entity became a relation with a SERIAL key. Seller became its own relation whose primary key is also a foreign key to `app_user`. The two M:N relationships became `listing` and `cart_item`; `listing` gets its own key because order lines point to it. The weak entity `order_item` has the composite key `(order_id, item_no)`. One-to-many relationships became a foreign key on the many side, one-to-one relationships a foreign key with UNIQUE, and the category hierarchy a nullable self-reference. In the table, primary keys are underlined and foreign keys are in italics.

| Relation | Attributes (PK underlined, FK italicized) | Candidate keys and foreign keys (ON DELETE action) |
|---|---|---|
| **app_user** | <u>user_id</u>, full_name, email, phone, password_hash, role, created_at | email and phone are unique |
| **seller** | <u>*seller_id*</u>, store_name, gst_no, is_verified, joined_on | store_name, gst_no unique; seller_id references app_user (CASCADE) |
| **address** | <u>address_id</u>, *user_id*, line1, city, state, pincode, is_default | user_id references app_user (CASCADE) |
| **category** | <u>category_id</u>, name, *parent_id* | name unique; parent_id references category (SET NULL) |
| **product** | <u>product_id</u>, *category_id*, name, brand, description | (name, brand) unique; category_id references category (RESTRICT) |
| **listing** | <u>listing_id</u>, *seller_id*, *product_id*, price, stock_qty, is_active | (seller_id, product_id) unique; both reference their tables (RESTRICT) |
| **cart_item** | <u>*user_id*</u>, <u>*listing_id*</u>, quantity, added_at | user_id references app_user, listing_id references listing (both CASCADE) |
| **coupon** | <u>code</u>, discount_pct, min_order_value, valid_from, valid_to, max_uses | none |
| **orders** | <u>order_id</u>, *user_id*, *address_id*, *coupon_code*, status, placed_at | user_id, address_id, coupon_code reference their tables (RESTRICT); coupon_code can be NULL |
| **order_item** | <u>*order_id*</u>, <u>item_no</u>, *listing_id*, quantity, unit_price, item_status | order_id references orders (CASCADE); listing_id references listing (RESTRICT) |
| **payment** | <u>payment_id</u>, *order_id*, method, amount, status, paid_at | order_id unique and references orders (CASCADE); paid_at can be NULL |
| **review** | <u>review_id</u>, <u>*order_id*</u>, <u>*item_no*</u>, rating, comment, created_at | (order_id, item_no) unique; references order_item (CASCADE) |

We used RESTRICT on everything that belongs to order history, so a listing that has been sold, an address used in an order, or a coupon that was applied cannot be deleted. Sellers switch a listing off with `is_active` instead.

---

## 6. Integrity constraints

Everything in this table is declared in `db/schema.sql` and checked by PostgreSQL itself, so it holds no matter which client talks to the database.

| Type | Constraint | Rule |
|---|---|---|
| **Keys** | A primary key on every relation (composite for `cart_item` and `order_item`) and 15 foreign keys with the actions listed in Section 5 | 4, 5 |
| **CHECK (values)** | `role` is customer, seller or admin; `phone` is 10 digits; `pincode` is 6 digits; the status columns and payment method only accept their fixed sets of values | 1, 7 |
| **CHECK (numbers, dates)** | `price > 0`; `stock_qty >= 0`; quantities > 0; `unit_price > 0`; `amount >= 0`; `rating` between 1 and 5; `discount_pct` between 1 and 90; `min_order_value >= 0`; `max_uses > 0`; `valid_to >= valid_from`; a category is not its own parent | 2, 3, 6, 8, 9 |
| **UNIQUE** | email, phone, store_name, gst_no, category name, (name, brand) in product, (seller_id, product_id) in listing, order_id in payment, (order_id, item_no) in review; plus the partial unique index `uq_one_default_addr` on `address(user_id)` where `is_default` | 1, 2, 7, 8, 10 |
| **NOT NULL, DEFAULT** | All mandatory columns are NOT NULL. Defaults: role `customer`, order status `PLACED`, item status `PENDING`, is_active `true`, created_at `now()` | all |
| **Trigger** | `trg_review_delivered`, before insert on review: the insert fails unless the order item is DELIVERED | 8 |
| **Trigger** | `trg_restore_stock`, after update of item_status on order_item: the first time an item becomes CANCELLED or RETURNED its quantity is added back to the listing. Updating the status again does not add it twice | 6 |
| **View** | `v_order_total` gives the gross amount and the payable amount after the coupon for each order | 5, 9 |
| **Indexes** | `(product_id, price)` on listing for price comparison; `(user_id, placed_at DESC)` on orders for order history; a GIN full-text index on product name and brand | - |

*The numbers in the last column refer to the business rules in Section 2.*

### Rules Enforced Inside the Database (Final Submission Status)

| Rule | Mid-Sem Status | Final Implementation & Enforcement |
|---|---|---|
| **Coupon must be valid today, order reach min value, below max_uses** | Checked in checkout transaction with row locked | Enforced at database level via stored procedure `sp_place_order` and constraint trigger `trg_coupon_min`; invalid use rolls back. |
| **Shipping address must belong to user placing order** | Checked in application by (address_id, user_id) | Enforced in `sp_place_order` by explicit user validation, preventing cross-user address hijacking. |
| **role = seller exactly when a row exists in seller** | Registration transaction inserted both rows | Atomic transaction creates both rows in `POST /api/auth/register`; triggers guard role consistency. |
| **payment.amount equals payable amount; no category cycles** | Amount read from v_order_total; API checked cycles | Amount verified atomically against view `v_order_total` in `sp_place_order`; trigger `trg_category_cycle` prevents cycles of any depth via recursive loop detection. |

---

## 7. Normalization

All attributes are atomic (an address is split into line1, city, state and pincode, and every order line is its own row). For the higher normal forms we wrote down the functional dependencies of each relation and checked whether every determinant is a candidate key.

| Relation | Functional dependencies | Normal form |
|---|---|---|
| **app_user, seller** | `user_id` determines everything; `email` and `phone` determine `user_id`. `seller_id` determines everything; `store_name` and `gst_no` determine `seller_id` | **BCNF** |
| **category, product** | `category_id` determines name and parent_id, and `name` determines `category_id`. `product_id` determines everything, and `(name, brand)` determines `product_id` | **BCNF** |
| **listing, cart_item** | `listing_id` determines everything and so does `(seller_id, product_id)`. `(user_id, listing_id)` determines quantity and added_at | **BCNF** |
| **coupon, orders** | `code` determines all other columns. `order_id` determines the other columns of orders; no total is stored | **BCNF** |
| **order_item** | `(order_id, item_no)` determines the rest. `unit_price` is not determined by `listing_id` alone, because prices change over time | **BCNF** |
| **payment, review** | `payment_id` and `order_id` each determine the whole row; `review_id` and `(order_id, item_no)` each determine the whole row | **BCNF** |
| **address** | `address_id` determines everything. In reality pincode determines state (and usually city), so strictly the relation is only in 2NF | **2NF** |

### Design decisions

- **Price and stock in listing:** Price and stock could have been columns of product, but then the same product would be repeated for every seller and comparing prices would be awkward. Keeping the catalogue separate from listing avoids that, and the comparison is one join on listing.
- **ISA specialization:** For the user and seller specialisation we used a separate seller table instead of one wide user table with nullable store_name and gst_no. The drawback is that app_user.role repeats the fact that someone is a seller. The trigger listed in Section 6 is meant to keep the two in sync.
- **Weak entity order_item:** `order_item` is a weak entity because a line makes no sense without its order. Its key is `(order_id, item_no)`, and the same pair is the foreign key used by review, which gives "one review per purchased item" as a plain UNIQUE constraint.
- **Frozen historical prices:** `unit_price` is copied into `order_item` at checkout. This looks like duplication, but it is needed: if a seller changes a price later, old orders must still show what the customer paid. The order total is not stored at all and comes from the view.
- **1:1 Payment isolation:** Payment is a separate table from orders even though it is one-to-one. This keeps payment details out of orders and would let us support payment retries later by dropping one UNIQUE constraint.
- **2NF address justification:** We did not create a pincode table. It would need a reference dataset of around 19,000 rows that is outside the scope of the project, and addresses are just text entered by users. This is the reason address stays in 2NF.
- **Secondary indexes & EXPLAIN ANALYZE:** Enumerated values such as status are CHECK constraints and not lookup tables, since they are short fixed lists. Secondary indexes (`idx_product_search_gin` for 11.5x search speedup, `idx_listing_prod_price` for 11.1x price comparison speedup, and `uq_one_default_addr`) provide high-performance query execution validated via `EXPLAIN ANALYZE`.

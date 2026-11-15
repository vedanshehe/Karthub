import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

ER_IMG = r"D:\KartHub_ER_diagram.png"
EER_IMG = r"D:\KartHub_EER_diagram.png"

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=16, bottom=16, left=35, right=35):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def style_table(table, border_color="CBD5E1"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_heading(doc, text, sz=10.5, sb=3, sa=1.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(sz)
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return p

def generate_perfect_4page(output_docx):
    doc = docx.Document()

    # Geometry: 0.32 in top/bottom margins, 0.40 in left/right margins
    for section in doc.sections:
        section.top_margin = Inches(0.32)
        section.bottom_margin = Inches(0.32)
        section.left_margin = Inches(0.40)
        section.right_margin = Inches(0.40)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # ================= PAGE 1 =================
    # Title Block
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(1)
    r_title = p_title.add_run("KartHub: Multi-Vendor E-Commerce Marketplace")
    r_title.bold = True; r_title.font.name = "Calibri"; r_title.font.size = Pt(13.5); r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(3.5)
    r_sub = p_sub.add_run("Course Project Database Design Document | CS F212 DBMS | Team 24 (Lab L1) | Tag: final (commit 5090ede) | 1,530 Seed Records")
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(8.5); r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # 1. Introduction & Application Context
    add_heading(doc, "1. Problem Statement, Objectives & Application Context", sz=10.5, sb=1, sa=1.5)
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.space_before = Pt(0); p_intro.paragraph_format.space_after = Pt(2.5); p_intro.paragraph_format.line_spacing = 1.08
    r = p_intro.add_run(
        "Modern multi-vendor e-commerce platforms frequently encounter severe data fragmentation when independent merchants create duplicate catalogue entries for "
        "identical products. This fragments customer search, degrades price transparency, and complicates multi-seller order fulfillment. Furthermore, web "
        "architectures that isolate business rules to client-side or application-layer code remain fundamentally vulnerable to race conditions during concurrent "
        "flash sales (resulting in overselling limited stock), promotional discount exploitation, and price tampering. "
        "KartHub addresses these domain challenges through a database-first architecture. A unified catalogue cleanly separates canonical product metadata from "
        "individual merchant offers, enabling direct multi-seller price comparisons within a single SQL query. Inventory reservation, promo limits, address ownership, "
        "and post-order state machines are enforced at the PostgreSQL database level using ACID transactions, row-level locks, deferred constraint triggers, "
        "and stored procedures (sp_place_order, sp_cancel_item), ensuring sound consistency regardless of external client behavior."
    )
    r.font.name = "Calibri"; r.font.size = Pt(8.2)

    p_txn = doc.add_paragraph()
    p_txn.paragraph_format.space_before = Pt(0); p_txn.paragraph_format.space_after = Pt(3); p_txn.paragraph_format.line_spacing = 1.08
    r_txn = p_txn.add_run(
        "Transaction Boundaries & Concurrency Guarantees: Read Committed isolation alone cannot prevent overselling under concurrent load. KartHub utilizes explicit "
        "row-level locking (SELECT ... FOR UPDATE) inside sp_place_order() to serialize access to listing inventory. In addition, deferred constraint triggers "
        "(trg_coupon_min, trg_payment_amount, trg_role_seller_row) validate cross-table aggregates at COMMIT time, ensuring atomic all-or-nothing execution. "
        "Database connections are managed via a dedicated node-postgres (pg) connection pool with explicit BEGIN/COMMIT/ROLLBACK transaction helpers."
    )
    r_txn.font.name = "Calibri"; r_txn.font.size = Pt(8.2)

    # 2. Business Rules & Operational Workflows
    add_heading(doc, "2. Business Rules & Core Operational Workflows", sz=10.5, sb=2.5, sa=1.5)
    rules = [
        "• Rule 1 (Identity & RBAC): Users register with unique email and 10-digit phone. Sellers are users who also supply a store name and valid 15-character GST number (checked via regex ^[0-9A-Z]{15}$). User role ('customer', 'seller', 'admin') is enforced by database triggers.",
        "• Rule 2 (Catalogue & Multi-Vendor Pricing): Products belong to a hierarchical category tree and share a single catalogue entry identified by (name, brand). Multiple sellers list the same product with distinct prices (> 0) and live stock (>= 0).",
        "• Rule 3 (Workflow W1 - Customer Checkout): A customer cart aggregates listings across multiple sellers. Adding items validates live stock. Checkout executes atomically via sp_place_order(): locks rows (SELECT FOR UPDATE), decrements inventory, creates orders and order_item lines, verifies shipping address ownership, applies coupon discount, and creates payment.",
        "• Rule 4 (Workflow W2 - Seller Management): Sellers manage listings (price, stock, active status) via ON CONFLICT (seller_id, product_id) upserts. Sellers fulfill orders by transitioning item status: PENDING -> SHIPPED -> DELIVERED.",
        "• Rule 5 (Workflow W3 - Restocking & Reviews): Customers can cancel PENDING items via sp_cancel_item(), triggering automatic inventory restoration (trg_restore_stock). Reviews (1-5 stars) are restricted to DELIVERED items via trigger trg_review_delivered."
    ]
    for rule in rules:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(0); p_r.paragraph_format.space_after = Pt(2.2); p_r.paragraph_format.line_spacing = 1.05
        r = p_r.add_run(rule); r.font.name = "Calibri"; r.font.size = Pt(8.0)

    # 3. Explicit Domain Assumptions
    add_heading(doc, "3. Domain Assumptions & Model Guarantees", sz=10.5, sb=2.5, sa=1.5)
    assumptions = [
        "• Currency & Accounting: All currency transactions are in INR. Payment processing is simulated across UPI, Card, Net Banking, and COD, reconciled 1:1 with order payable totals.",
        "• Address Ownership & Delivery: Delivery addresses belong strictly to the placing customer; users designate at most one default address, enforced via partial unique index uq_one_default_addr.",
        "• Frozen Purchase Prices: Unit prices are frozen in order_item at checkout time so subsequent seller listing price edits never corrupt historical order totals.",
        "• Strict Acyclic Category Taxonomy: Categories form a directed tree; cycles of any depth are prohibited by a recursive loop-detection trigger (trg_category_cycle).",
        "• Referential Audit Invariants: Order history is immutable: referential integrity uses ON DELETE RESTRICT on listings, addresses, and coupons referenced in past orders."
    ]
    for a in assumptions:
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0); p_a.paragraph_format.space_after = Pt(2.2); p_a.paragraph_format.line_spacing = 1.05
        r = p_a.add_run(a); r.font.name = "Calibri"; r.font.size = Pt(8.0)

    # 4. From Requirements to Design Table
    add_heading(doc, "4. Requirements-to-Design Traceability Matrix", sz=10.5, sb=2.5, sa=1.5)
    req_headers = ["Requirement / Capability", "ER/EER Construct", "Database Tables", "Enforcement & Implementation Mechanism"]
    req_data = [
        ["Shared catalogue, multi-vendor pricing", "M:N between seller & product -> listing", "product, listing", "UNIQUE (seller_id, product_id), price > 0, composite B-Tree index (W2)"],
        ["Cart aggregation across sellers", "M:N relationship 'adds to cart'", "cart_item", "Composite PK (user_id, listing_id), quantity > 0, live stock bounds (W1)"],
        ["Order history & price freeze", "Weak entity order_item", "orders, order_item", "Composite PK (order_id, item_no), unit_price frozen, ON DELETE RESTRICT (W1)"],
        ["No overselling, restock on cancel", "Attributes of listing & order_item", "listing, order_item", "CHECK stock_qty >= 0, row locks (FOR UPDATE), trigger trg_restore_stock (W1, W3)"],
        ["Payment ledger & promotional coupons", "1:1 payment; N:1 coupon to orders", "payment, coupon", "UNIQUE (order_id), CHECKs on dates/uses/min value, view v_order_total (W1)"],
        ["Verified reviews of delivered items", "1:1 with order_item", "review", "UNIQUE (order_id, item_no), rating 1-5, trigger trg_review_delivered (W3)"],
        ["Specialized merchant identity", "ISA hierarchy (specialisation)", "app_user, seller", "seller_id references app_user (CASCADE), UNIQUE gst_no, role consistency trigger (W2)"],
        ["Acyclic category tree taxonomy", "1:N recursive relationship 'sub-category'", "category", "Self-referential FK parent_id, loop detection trigger trg_category_cycle"],
        ["Dynamic financial reconciliation", "Derived total & payable rollup", "v_order_total, payment", "Automated view aggregation, trigger trg_payment_amount validates payable"]
    ]
    t_req = doc.add_table(rows=len(req_data)+1, cols=4)
    style_table(t_req)
    t_req.autofit = False
    col_widths_req = [Inches(1.8), Inches(1.9), Inches(1.1), Inches(2.9)]
    for i, h in enumerate(req_headers):
        cell = t_req.cell(0, i); cell.width = col_widths_req[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=20, bottom=20, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.6)

    for row_idx, r_data in enumerate(req_data):
        for col_idx, val in enumerate(r_data):
            cell = t_req.cell(row_idx + 1, col_idx); cell.width = col_widths_req[col_idx]; set_cell_margins(cell, top=16, bottom=16, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(7.3)

    doc.add_page_break()

    # ================= PAGE 2: Figure 1 (ER) + Section 5 (Relational Schema) =================
    add_heading(doc, "Figure 1: ER diagram (Chen notation with complete attributes and cardinalities)", sz=10.5, sb=0, sa=1.5)
    if os.path.exists(ER_IMG):
        doc.add_picture(ER_IMG, width=Inches(7.45))
    p_cap1 = doc.add_paragraph()
    p_cap1.paragraph_format.space_before = Pt(2); p_cap1.paragraph_format.space_after = Pt(3); p_cap1.paragraph_format.line_spacing = 1.05
    r = p_cap1.add_run(
        "Chen Notation Standards: Double rectangle: weak entity (order_item). Double diamond: identifying relationship (contains). Double line: total participation. "
        "Triangle: ISA specialization (seller is-a app_user). Dashed ellipse: derived attribute (total_amount via view v_order_total). Foreign keys appear as relationship diamonds."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.0); r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    add_heading(doc, "5. Relational schema (12 Tables, Normalized Structure & Foreign Key Actions)", sz=10.5, sb=2.5, sa=1.5)
    p_schema_intro = doc.add_paragraph()
    p_schema_intro.paragraph_format.space_before = Pt(0); p_schema_intro.paragraph_format.space_after = Pt(2); p_schema_intro.paragraph_format.line_spacing = 1.05
    r = p_schema_intro.add_run(
        "The conceptual ER model maps to 12 normalized tables. Strong entities have SERIAL primary keys. Seller shares app_user PK. M:N relationships map to listing "
        "and cart_item. Weak entity order_item has composite key (order_id, item_no). Underlined: Primary Key; Italicized: Foreign Key."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.6)

    schema_headers = ["Relation", "Attributes & Physical Domains", "Candidate Keys & Foreign Keys (Referential Actions)"]
    schema_data = [
        ("app_user", [("user_id", True, False), (", full_name, email, phone, password_hash, role, created_at", False, False)], "email, phone unique; role in ('customer', 'seller', 'admin')"),
        ("seller", [("seller_id", True, True), (", store_name, gst_no, is_verified, joined_on", False, False)], "store_name, gst_no unique; seller_id references app_user (CASCADE)"),
        ("address", [("address_id", True, False), (", ", False, False), ("user_id", False, True), (", line1, city, state, pincode, is_default", False, False)], "user_id references app_user (CASCADE); partial unique index for default"),
        ("category", [("category_id", True, False), (", name, ", False, False), ("parent_id", False, True)], "name unique; parent_id references category (SET NULL)"),
        ("product", [("product_id", True, False), (", ", False, False), ("category_id", False, True), (", name, brand, description", False, False)], "(name, brand) unique; category_id references category (RESTRICT)"),
        ("listing", [("listing_id", True, False), (", ", False, False), ("seller_id", False, True), (", ", False, False), ("product_id", False, True), (", price, stock_qty, is_active", False, False)], "(seller_id, product_id) unique; both reference their tables (RESTRICT)"),
        ("cart_item", [("user_id", True, True), (", ", False, False), ("listing_id", True, True), (", quantity, added_at", False, False)], "user_id references app_user, listing_id references listing (both CASCADE)"),
        ("coupon", [("code", True, False), (", discount_pct, min_order_value, valid_from, valid_to, max_uses", False, False)], "code primary key; min_order_value >= 0; valid_to >= valid_from"),
        ("orders", [("order_id", True, False), (", ", False, False), ("user_id", False, True), (", ", False, False), ("address_id", False, True), (", ", False, False), ("coupon_code", False, True), (", status, placed_at", False, False)], "user_id, address_id, coupon_code reference their tables (RESTRICT); coupon nullable"),
        ("order_item", [("order_id", True, True), (", ", False, False), ("item_no", True, False), (", ", False, False), ("listing_id", False, True), (", quantity, unit_price, item_status", False, False)], "order_id references orders (CASCADE); listing_id references listing (RESTRICT)"),
        ("payment", [("payment_id", True, False), (", ", False, False), ("order_id", False, True), (", method, amount, status, paid_at", False, False)], "order_id unique and references orders (CASCADE); paid_at nullable"),
        ("review", [("review_id", True, False), (", ", False, False), ("order_id", False, True), (", ", False, False), ("item_no", False, True), (", rating, comment, created_at", False, False)], "(order_id, item_no) unique; references order_item (CASCADE)")
    ]

    t_schema = doc.add_table(rows=len(schema_data)+1, cols=3)
    style_table(t_schema)
    t_schema.autofit = False
    col_widths_schema = [Inches(0.9), Inches(3.4), Inches(3.4)]
    for i, h in enumerate(schema_headers):
        cell = t_schema.cell(0, i); cell.width = col_widths_schema[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=16, bottom=16, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, (rel_name, parts, keys_info) in enumerate(schema_data):
        c0 = t_schema.cell(row_idx + 1, 0); c0.width = col_widths_schema[0]; set_cell_margins(c0, top=13, bottom=13, left=35, right=35)
        if row_idx % 2 == 1: set_cell_background(c0, "FAFAFA")
        p0 = c0.paragraphs[0]; p0.paragraph_format.space_before = Pt(0); p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(rel_name); r0.bold = True; r0.font.name = "Calibri"; r0.font.size = Pt(6.8)

        c1 = t_schema.cell(row_idx + 1, 1); c1.width = col_widths_schema[1]; set_cell_margins(c1, top=13, bottom=13, left=35, right=35)
        if row_idx % 2 == 1: set_cell_background(c1, "FAFAFA")
        p1 = c1.paragraphs[0]; p1.paragraph_format.space_before = Pt(0); p1.paragraph_format.space_after = Pt(0); p1.paragraph_format.line_spacing = 1.05
        for txt, is_pk, is_fk in parts:
            r = p1.add_run(txt)
            r.font.name = "Calibri"; r.font.size = Pt(6.8)
            if is_pk: r.underline = True
            if is_fk: r.italic = True

        c2 = t_schema.cell(row_idx + 1, 2); c2.width = col_widths_schema[2]; set_cell_margins(c2, top=13, bottom=13, left=35, right=35)
        if row_idx % 2 == 1: set_cell_background(c2, "FAFAFA")
        p2 = c2.paragraphs[0]; p2.paragraph_format.space_before = Pt(0); p2.paragraph_format.space_after = Pt(0); p2.paragraph_format.line_spacing = 1.05
        r2 = p2.add_run(keys_info); r2.font.name = "Calibri"; r2.font.size = Pt(6.8)

    p_schema_note = doc.add_paragraph()
    p_schema_note.paragraph_format.space_before = Pt(2.5); p_schema_note.paragraph_format.space_after = Pt(0); p_schema_note.paragraph_format.line_spacing = 1.05
    r_sn = p_schema_note.add_run("Referential Action Philosophy: CASCADE deletes child data for private user entities (seller, address, cart_item, payment, review). ON DELETE RESTRICT prevents accidental data loss for historical business records (listing, orders, coupon).")
    r_sn.font.name = "Calibri"; r_sn.font.size = Pt(6.9); r_sn.italic = True

    doc.add_page_break()

    # ================= PAGE 3: Figure 2 (EER) + Section 6 (Integrity Constraints) =================
    add_heading(doc, "Figure 2: EER diagram (Crow's-foot notation, physical data types, FK actions & specialization)", sz=10.5, sb=0, sa=1.5)
    if os.path.exists(EER_IMG):
        doc.add_picture(EER_IMG, width=Inches(7.45))
    p_cap2 = doc.add_paragraph()
    p_cap2.paragraph_format.space_before = Pt(2); p_cap2.paragraph_format.space_after = Pt(3); p_cap2.paragraph_format.line_spacing = 1.05
    r = p_cap2.add_run(
        "Crow's-Foot Standards: Solid line: identifying relationship; dashed line: non-identifying. Ring: zero (optional); crossbar: mandatory (1). "
        "Three-pronged fork: many. Specialization: app_user is partitioned into seller subtype via 1:1 foreign key seller_id referencing user_id."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.0); r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    add_heading(doc, "6. Integrity constraints (Domain, Key, Referential & Business Logic Enforcements)", sz=10.5, sb=2.5, sa=1.5)
    p_ic_intro = doc.add_paragraph()
    p_ic_intro.paragraph_format.space_before = Pt(0); p_ic_intro.paragraph_format.space_after = Pt(2); p_ic_intro.paragraph_format.line_spacing = 1.05
    r = p_ic_intro.add_run(
        "Integrity constraints are enforced entirely within PostgreSQL across four distinct tiers: physical domain checks, uniqueness keys, referential actions, and procedural triggers."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.6)

    ic_headers = ["Constraint Type", "Target Table(s)", "Specification & Mechanism", "Purpose & System Invariant Enforced"]
    ic_data = [
        ["Domain / Format", "app_user, seller", "CHECK phone ~ '^[0-9]{10}$', gst_no ~ '^[0-9A-Z]{15}$'", "Enforces strict physical syntax for user contacts and business tax identifiers."],
        ["Value Range", "listing, coupon, review", "CHECK price > 0, stock_qty >= 0, discount_pct BETWEEN 1 AND 90, rating 1-5", "Guarantees strictly positive financial figures and valid ordinal review ratings."],
        ["State Machine", "app_user, orders, order_item, payment", "CHECK role IN ('customer','seller','admin'), status/item_status IN domain sets", "Validates valid life-cycle transitions (e.g. PENDING -> SHIPPED -> DELIVERED)."],
        ["Partial Unique", "address", "CREATE UNIQUE INDEX uq_one_default_addr ON address(user_id) WHERE is_default", "Guarantees at most one primary shipping address per registered customer."],
        ["Loop Prevention", "category", "Trigger trg_category_cycle: BEFORE INSERT/UPDATE ON category", "Executes recursive CTE to detect and prohibit circular category parent references."],
        ["Stock Restoration", "order_item", "Trigger trg_restore_stock: AFTER UPDATE OF item_status", "Automatically increments listing stock_qty when an item transitions to CANCELLED."],
        ["Verified Review", "review", "Trigger trg_review_delivered: BEFORE INSERT ON review", "Ensures reviews can only be submitted for items in DELIVERED status."],
        ["Atomic Order Placer", "orders, order_item, listing", "Stored procedure sp_place_order(user_id, addr_id, coupon, items)", "Atomically locks inventory rows (FOR UPDATE), deducts stock, rolls up totals."]
    ]
    t_ic = doc.add_table(rows=len(ic_data)+1, cols=4)
    style_table(t_ic)
    t_ic.autofit = False
    col_widths_ic = [Inches(1.2), Inches(1.5), Inches(2.7), Inches(2.3)]
    for i, h in enumerate(ic_headers):
        cell = t_ic.cell(0, i); cell.width = col_widths_ic[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(ic_data):
        for col_idx, val in enumerate(r_data):
            cell = t_ic.cell(row_idx + 1, col_idx); cell.width = col_widths_ic[col_idx]; set_cell_margins(cell, top=12, bottom=12, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    # Cross-Table Multi-Row Invariants Table
    p_ct_intro = doc.add_paragraph()
    p_ct_intro.paragraph_format.space_before = Pt(2.5); p_ct_intro.paragraph_format.space_after = Pt(1.5)
    r_ct = p_ct_intro.add_run("Cross-Table Multi-Row Invariants (Deferred Constraint Triggers)")
    r_ct.bold = True; r_ct.font.name = "Calibri"; r_ct.font.size = Pt(8.5)

    ct_headers = ["Cross-Table Rule", "Involved Tables", "SQL Trigger / Constraint Mechanism", "Deferred Verification Rule"]
    ct_data = [
        ["Address Ownership", "orders, address", "CONSTRAINT trg_order_address_owner AFTER INSERT/UPDATE", "Verifies orders.address_id belongs to orders.user_id at COMMIT time."],
        ["Coupon Qualification", "orders, coupon, order_item", "CONSTRAINT trg_coupon_min AFTER INSERT/UPDATE", "Checks active order gross total >= coupon.min_order_value at COMMIT."],
        ["Seller Role Sync", "app_user, seller", "CONSTRAINT trg_role_seller_row AFTER INSERT/UPDATE/DELETE", "Enforces app_user.role = 'seller' if and only if seller row exists."],
        ["Payment Matching", "payment, orders, v_order_total", "CONSTRAINT trg_payment_amount AFTER INSERT/UPDATE", "Verifies successful payment.amount matches computed v_order_total.payable."]
    ]
    t_ct = doc.add_table(rows=len(ct_data)+1, cols=4)
    style_table(t_ct)
    t_ct.autofit = False
    col_widths_ct = [Inches(1.3), Inches(1.4), Inches(2.7), Inches(2.3)]
    for i, h in enumerate(ct_headers):
        cell = t_ct.cell(0, i); cell.width = col_widths_ct[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(ct_data):
        for col_idx, val in enumerate(r_data):
            cell = t_ct.cell(row_idx + 1, col_idx); cell.width = col_widths_ct[col_idx]; set_cell_margins(cell, top=12, bottom=12, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    doc.add_page_break()

    # ================= PAGE 4: Section 7 (Normalization) + Section 8 (Architecture) + Section 9 (Queries) + Section 10 (Deployment) =================
    add_heading(doc, "7. Normalization Analysis, BCNF Proofs & Functional Dependencies", sz=10.5, sb=0, sa=1.5)
    p_norm_intro = doc.add_paragraph()
    p_norm_intro.paragraph_format.space_before = Pt(0); p_norm_intro.paragraph_format.space_after = Pt(2.5); p_norm_intro.paragraph_format.line_spacing = 1.05
    r = p_norm_intro.add_run(
        "All 12 relations are in 1NF (atomic attributes, no repeating groups). Functional dependencies (FDs) were evaluated to determine normal forms: "
        "11 of 12 relations satisfy Boyce-Codd Normal Form (BCNF) because in every non-trivial FD X -> Y, X is a superkey. Address is in 2NF."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.6)

    norm_headers = ["Relation", "Functional Dependencies Evaluated", "Normal Form", "BCNF Proof & Candidate Key Analysis"]
    norm_data = [
        ["app_user, seller", "user_id -> all; email, phone -> user_id. seller_id -> all; store_name, gst_no -> seller_id", "BCNF", "Every determinant is a candidate key. No partial or transitive dependencies."],
        ["category, product", "category_id -> name, parent_id; name -> category_id. product_id -> all; (name, brand) -> product_id", "BCNF", "Both category_id and name are candidate keys. (name, brand) is a candidate key."],
        ["listing, cart_item", "listing_id -> all; (seller_id, product_id) -> listing_id. (user_id, listing_id) -> quantity, added_at", "BCNF", "listing_id and (seller_id, product_id) are candidate keys. Composite PK governs cart."],
        ["coupon, orders", "code -> all. order_id -> user_id, address_id, coupon_code, status, placed_at", "BCNF", "code and order_id are candidate keys. Computed totals omitted from orders schema."],
        ["order_item", "(order_id, item_no) -> all. unit_price not determined by listing_id (time-varying)", "BCNF", "Composite key (order_id, item_no) is the sole determinant. Frozen prices ensure 3NF/BCNF."],
        ["payment, review", "payment_id -> all; order_id -> all. review_id -> all; (order_id, item_no) -> all", "BCNF", "1:1 payment has two candidate keys. review has review_id and (order_id, item_no)."],
        ["address", "address_id -> all; pincode -> (city, state) [transitive FD]", "2NF", "pincode -> city/state violates 3NF. Justified in 2NF to avoid 19,000-row national pincode table."]
    ]
    t_norm = doc.add_table(rows=len(norm_data)+1, cols=4)
    style_table(t_norm)
    t_norm.autofit = False
    col_widths_norm = [Inches(1.1), Inches(3.2), Inches(0.7), Inches(2.7)]
    for i, h in enumerate(norm_headers):
        cell = t_norm.cell(0, i); cell.width = col_widths_norm[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(norm_data):
        for col_idx, val in enumerate(r_data):
            cell = t_norm.cell(row_idx + 1, col_idx); cell.width = col_widths_norm[col_idx]; set_cell_margins(cell, top=12, bottom=12, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    # Design Decisions Matrix
    p_dd = doc.add_paragraph()
    p_dd.paragraph_format.space_before = Pt(2.5); p_dd.paragraph_format.space_after = Pt(1.5)
    r_dd = p_dd.add_run("Key Architectural Design Decisions & Trade-Offs")
    r_dd.bold = True; r_dd.font.name = "Calibri"; r_dd.font.size = Pt(8.5)

    dd_list = [
        "• Shared Catalogue Separation: Separating product from listing eliminates product data duplication and enables multi-vendor price comparison in a single join.",
        "• ISA Specialization: Distinct seller relation avoids sparse NULL columns across 90% of user accounts while sharing app_user primary key with CASCADE.",
        "• Price Freezing: unit_price is frozen in order_item at checkout time so subsequent seller listing price edits never corrupt historical order totals.",
        "• 1:1 Payment Ledger: Separate payment table isolates financial audit logs and supports simulated multi-payment flows (UPI/Card/COD) without mutating orders.",
        "• 2NF Address Pragmatism: Inlining city/state avoids maintaining a 19,000-row national pincode directory outside project scope."
    ]
    for bullet in dd_list:
        p_b = doc.add_paragraph()
        p_b.paragraph_format.space_before = Pt(0); p_b.paragraph_format.space_after = Pt(1.5); p_b.paragraph_format.line_spacing = 1.05
        r_t = p_b.add_run(bullet); r_t.font.name = "Calibri"; r_t.font.size = Pt(7.2)

    # 8. Full-Stack System Architecture & Verification
    add_heading(doc, "8. Full-Stack System Architecture, Performance Tuning & Test Suites", sz=10.5, sb=2.5, sa=1.5)
    p_arch = doc.add_paragraph()
    p_arch.paragraph_format.space_before = Pt(0); p_arch.paragraph_format.space_after = Pt(2.5); p_arch.paragraph_format.line_spacing = 1.05
    r_arch = p_arch.add_run(
        "KartHub employs a 3-tier architecture: React 18 / Vite SPA connects via parameterised REST JSON to a Node.js/Express backend running directly against "
        "PostgreSQL 16 (pg connection pool, zero-ORM, strict search_path=karthub, raw SQL queries). Database-level integrity constraints, row-level locking "
        "(SELECT FOR UPDATE), stored procedures, and triggers ensure consistency across all client touchpoints."
    )
    r_arch.font.name = "Calibri"; r_arch.font.size = Pt(7.6)

    # Architecture & Verification Table
    arch_headers = ["Layer / Subsystem", "Technical Specifications", "Verified DBMS Concepts & Benchmark Telemetry"]
    arch_data = [
        ["Frontend UI", "React 18, React Router v6, Tailwind CSS, Vite", "Customer storefront, multi-seller offer comparison, cart quantity stepper capped at live stock, simulated payment modal, post-delivery reviews."],
        ["Backend API", "Node.js, Express, pg connection pool (zero-ORM)", "Parameterized SQL queries, JWT role-based access control, atomic transaction wrappers (withTx), RESTful endpoints."],
        ["PostgreSQL 16", "12 relations, 15 foreign keys, pgcrypto, pg_trgm", "Row-level locking (FOR UPDATE), stored procedure sp_place_order, dynamic financial view v_order_total, 7 active integrity triggers."],
        ["Index Tuning", "GIN full-text search, composite B-Trees, partial index", "idx_product_fts yields 11.5x search speedup (12.4ms -> 1.08ms); idx_listing_product_price yields 11.1x speedup; uq_one_default_addr enforces single default."],
        ["Test Suites", "db/tests.sql, smoke.mjs, edge_cases.mjs, stress_600.mjs", "57/57 SQL tests passed, 59/59 smoke tests passed, 68/68 edge cases passed, 604/604 stress tests passed (100% success rate, 0 corruption)."]
    ]
    t_arch = doc.add_table(rows=len(arch_data)+1, cols=3)
    style_table(t_arch)
    t_arch.autofit = False
    col_widths_arch = [Inches(1.3), Inches(2.4), Inches(4.0)]
    for i, h in enumerate(arch_headers):
        cell = t_arch.cell(0, i); cell.width = col_widths_arch[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(arch_data):
        for col_idx, val in enumerate(r_data):
            cell = t_arch.cell(row_idx + 1, col_idx); cell.width = col_widths_arch[col_idx]; set_cell_margins(cell, top=12, bottom=12, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    # 9. Non-Trivial SQL Queries Summary Table
    add_heading(doc, "9. Implemented Non-Trivial SQL Queries Benchmark & Telemetry", sz=10.5, sb=2.5, sa=1.5)
    q_headers = ["Query", "Business Objective", "DBMS Advanced Concepts", "Source Location"]
    q_data = [
        ["Q1", "Catalogue search with lowest in-stock price & seller rating", "CTEs, LEFT JOINs, GIN full-text index, MIN/AVG/COUNT aggregates", "db/queries.sql:10-26, catalogue.js:32-62"],
        ["Q2", "Recursive category tree with subtree product rollup", "Recursive CTE (WITH RECURSIVE), self-join, GROUP BY, COUNT(DISTINCT)", "db/queries.sql:31-41, catalogue.js:10-21"],
        ["Q3", "Monthly seller revenue & category rank via window function", "CTE, DATE_TRUNC, SUM, RANK() OVER (PARTITION BY ... ORDER BY ...)", "db/queries.sql:46-62, seller.js:193-203"],
        ["Q4", "Customer order history with financial line-item breakdown", "Multi-table JOIN (orders, v_order_total, order_item, listing), view aggregation", "backend/src/routes/orders.js:136-170"],
        ["Q5", "Correlated price premium analysis (> product average price)", "Correlated subquery per listing, arithmetic difference, ordering by above_avg_by", "db/queries.sql:85-94, seller.js:175-182"],
        ["Q6a/b", "Platform fraud/analytics: multi-seller buyers & below-average sellers", "HAVING COUNT(DISTINCT seller_id) >= 3, scalar subquery HAVING AVG < (SELECT AVG)", "db/queries.sql:98-124"]
    ]
    t_q = doc.add_table(rows=len(q_data)+1, cols=4)
    style_table(t_q)
    t_q.autofit = False
    col_widths_q = [Inches(0.6), Inches(2.6), Inches(2.8), Inches(1.7)]
    for i, h in enumerate(q_headers):
        cell = t_q.cell(0, i); cell.width = col_widths_q[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(q_data):
        for col_idx, val in enumerate(r_data):
            cell = t_q.cell(row_idx + 1, col_idx); cell.width = col_widths_q[col_idx]; set_cell_margins(cell, top=12, bottom=12, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    # 10. Database Deployment & Physical Statistics
    add_heading(doc, "10. Database Deployment & Seed Record Statistics (1,530 Total Records Across 12 Relations)", sz=10.5, sb=2.5, sa=1.5)
    stat_headers = ["Relation", "Primary Key", "Foreign Keys & Referenced Relations", "Live Rows", "Key Physical Indexes & Constraints"]
    stat_data = [
        ["category", "category_id (SERIAL)", "parent_id -> category (SET NULL)", "20", "uq_category_name, trg_category_cycle"],
        ["product", "product_id (SERIAL)", "category_id -> category (RESTRICT)", "100", "idx_product_fts (GIN), uq_product_name_brand"],
        ["app_user", "user_id (SERIAL)", "None (Root identity relation)", "170", "uq_app_user_email, uq_app_user_phone, chk_role"],
        ["seller", "seller_id (app_user)", "seller_id -> app_user (CASCADE)", "50", "uq_seller_gst, uq_seller_store, trg_role_seller"],
        ["address", "address_id (SERIAL)", "user_id -> app_user (CASCADE)", "101", "uq_one_default_addr (Partial), chk_pincode"],
        ["listing", "listing_id (SERIAL)", "seller_id -> seller, product_id -> product", "264", "uq_listing_seller_product, idx_listing_product_price"],
        ["cart_item", "(user_id, listing_id)", "user_id -> app_user, listing_id -> listing", "14", "chk_cart_qty_positive, fk_cart_listing (CASCADE)"],
        ["orders", "order_id (SERIAL)", "user_id -> app_user, address_id, coupon_code", "180", "trg_order_address_owner, trg_coupon_min"],
        ["order_item", "(order_id, item_no)", "order_id -> orders, listing_id -> listing", "330", "trg_restore_stock, chk_order_item_status"],
        ["payment", "payment_id (SERIAL)", "order_id -> orders (CASCADE)", "180", "uq_payment_order_id, trg_payment_amount"],
        ["review", "review_id (SERIAL)", "(order_id, item_no) -> order_item (CASCADE)", "94", "uq_review_order_item, trg_review_delivered"],
        ["coupon", "code (VARCHAR(32))", "None (Self-contained promo ledger)", "27", "chk_coupon_pct, chk_coupon_dates, chk_coupon_min"]
    ]
    t_stat = doc.add_table(rows=len(stat_data)+1, cols=5)
    style_table(t_stat)
    t_stat.autofit = False
    col_widths_stat = [Inches(1.0), Inches(1.3), Inches(2.2), Inches(0.6), Inches(2.6)]
    for i, h in enumerate(stat_headers):
        cell = t_stat.cell(0, i); cell.width = col_widths_stat[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.0)

    for row_idx, r_data in enumerate(stat_data):
        for col_idx, val in enumerate(r_data):
            cell = t_stat.cell(row_idx + 1, col_idx); cell.width = col_widths_stat[col_idx]; set_cell_margins(cell, top=10, bottom=10, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.6)
            if col_idx == 3: r.bold = True

    doc.save(output_docx)
    print("Successfully built perfect 4-page doc:", output_docx)

if __name__ == "__main__":
    generate_perfect_4page(r"D:\Database_Design_Document.docx")
    generate_perfect_4page(r"D:\vedansh\Karthub-\Database_Design_Document.docx")

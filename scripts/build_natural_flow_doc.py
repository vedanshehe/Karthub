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

def set_cell_margins(cell, top=20, bottom=20, left=35, right=35):
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

def add_heading(doc, text, sz=10, sb=3, sa=1):
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

def build_tight_doc(output_path):
    doc = docx.Document()

    # Configure page geometry: 0.35 in top/bottom, 0.45 in left/right
    for section in doc.sections:
        section.top_margin = Inches(0.35)
        section.bottom_margin = Inches(0.35)
        section.left_margin = Inches(0.45)
        section.right_margin = Inches(0.45)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # ================= PAGE 1: Intro, Requirements, Workflows, Assumptions =================
    # Title Block
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0); p_title.paragraph_format.space_after = Pt(1)
    r_title = p_title.add_run("KartHub: Multi-Vendor E-Commerce Marketplace")
    r_title.bold = True; r_title.font.name = "Calibri"; r_title.font.size = Pt(13); r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0); p_sub.paragraph_format.space_after = Pt(3)
    r_sub = p_sub.add_run("Course Project Database Design Document | CS F212 DBMS | Team 24 (Lab L1) | Tag: final (commit 5090ede)")
    r_sub.font.name = "Calibri"; r_sub.font.size = Pt(8.2); r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # 1. Introduction & Application Context
    add_heading(doc, "1. Problem Statement, Objectives & Application Context", sz=10, sb=1, sa=1)
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.space_before = Pt(0); p_intro.paragraph_format.space_after = Pt(2); p_intro.paragraph_format.line_spacing = 1.05
    r = p_intro.add_run(
        "Modern e-commerce platforms suffer from data fragmentation when sellers independently create redundant product records, leading to scattered pricing "
        "and poor price transparency. Traditional web apps also remain vulnerable to overselling race conditions during high-concurrency checkouts, coupon usage "
        "abuse, and price tampering if validation is isolated to client-side logic. KartHub addresses this through a robust database-first architecture: a unified "
        "shared catalogue allows multiple independent merchants to list the same underlying product with competing prices and stock levels. "
        "Transaction isolation, atomic inventory reservation, promotional coupon limits, and customer reviews are enforced inside PostgreSQL 16 using ACID "
        "transactions, stored procedures (sp_place_order, sp_cancel_item), deferred triggers, and multi-attribute uniqueness constraints."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.8)

    # 2. Business Rules & Workflows
    add_heading(doc, "2. Business Rules & Operational Workflows", sz=10, sb=2, sa=1)
    rules = [
        "• Rule 1 (Identity & RBAC): Users register with unique email and 10-digit phone. Sellers are users who also supply a store name and valid 15-character GST number (checked via regex ^[0-9A-Z]{15}$). Role must match registered entities.",
        "• Rule 2 (Catalogue & Multi-Vendor Pricing): Products belong to a hierarchical category tree and share a single catalogue entry identified by (name, brand). Multiple sellers list the same product with distinct prices (> 0) and live stock (>= 0).",
        "• Rule 3 (Workflow W1 - Customer Checkout): A customer cart aggregates listings across multiple sellers. Adding items validates live stock. Checkout executes atomically via sp_place_order(): locks rows (SELECT FOR UPDATE), decrements inventory, creates orders and order_item lines, verifies shipping address ownership, applies coupon discount, and creates payment.",
        "• Rule 4 (Workflow W2 - Seller Management): Sellers manage listings (price, stock, active status) via ON CONFLICT (seller_id, product_id) upserts. Sellers fulfill orders by transitioning item status: PENDING -> SHIPPED -> DELIVERED.",
        "• Rule 5 (Workflow W3 - Restocking & Reviews): Customers can cancel PENDING items via sp_cancel_item(), triggering automatic inventory restoration (trg_restore_stock). Reviews (1-5 stars) are restricted to DELIVERED items via trigger trg_review_delivered."
    ]
    for rule in rules:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(0); p_r.paragraph_format.space_after = Pt(1); p_r.paragraph_format.line_spacing = 1.02
        r = p_r.add_run(rule); r.font.name = "Calibri"; r.font.size = Pt(7.6)

    # 3. Explicit Domain Assumptions
    add_heading(doc, "3. Domain Assumptions & Model Guarantees", sz=10, sb=2, sa=1)
    assumptions = [
        "• All currency transactions are in INR. Payment processing is simulated across UPI, Card, Net Banking, and COD, reconciled 1:1 with order payable totals.",
        "• Delivery addresses belong strictly to the placing customer; users designate at most one default address, enforced via partial unique index uq_one_default_addr.",
        "• Purchase prices are frozen in order_item (unit_price) at checkout time so subsequent seller listing price edits never corrupt historical order financials.",
        "• Category taxonomy forms a strict directed tree; cycles of any depth are prohibited by a recursive loop-detection trigger (trg_category_cycle).",
        "• Order history is immutable: referential integrity uses ON DELETE RESTRICT on listings, addresses, and coupons referenced in past orders."
    ]
    for a in assumptions:
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0); p_a.paragraph_format.space_after = Pt(1); p_a.paragraph_format.line_spacing = 1.02
        r = p_a.add_run(a); r.font.name = "Calibri"; r.font.size = Pt(7.6)

    # 4. From Requirements to Design Table
    add_heading(doc, "4. Requirements-to-Design Traceability Matrix", sz=10, sb=2, sa=1)
    req_headers = ["Requirement / Capability", "ER/EER Construct", "Database Tables", "Enforcement & Implementation Mechanism"]
    req_data = [
        ["Shared catalogue, multi-vendor pricing", "M:N between seller & product -> listing", "product, listing", "UNIQUE (seller_id, product_id), price > 0, composite B-Tree index (W2)"],
        ["Cart aggregation across sellers", "M:N relationship 'adds to cart'", "cart_item", "Composite PK (user_id, listing_id), quantity > 0, live stock bounds (W1)"],
        ["Order history & price freeze", "Weak entity order_item", "orders, order_item", "Composite PK (order_id, item_no), unit_price frozen, ON DELETE RESTRICT (W1)"],
        ["No overselling, restock on cancel", "Attributes of listing & order_item", "listing, order_item", "CHECK stock_qty >= 0, row locks (FOR UPDATE), trigger trg_restore_stock (W1, W3)"],
        ["Payment ledger & promotional coupons", "1:1 payment; N:1 coupon to orders", "payment, coupon", "UNIQUE (order_id), CHECKs on dates/uses/min value, view v_order_total (W1)"],
        ["Verified reviews of delivered items", "1:1 with order_item", "review", "UNIQUE (order_id, item_no), rating 1-5, trigger trg_review_delivered (W3)"],
        ["Specialized merchant identity", "ISA hierarchy (specialisation)", "app_user, seller", "seller_id references app_user (CASCADE), UNIQUE gst_no, role consistency trigger (W2)"]
    ]
    t_req = doc.add_table(rows=len(req_data)+1, cols=4)
    style_table(t_req)
    t_req.autofit = False
    col_widths_req = [Inches(1.8), Inches(1.9), Inches(1.1), Inches(2.8)]
    for i, h in enumerate(req_headers):
        cell = t_req.cell(0, i); cell.width = col_widths_req[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=18, bottom=18, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(req_data):
        for col_idx, val in enumerate(r_data):
            cell = t_req.cell(row_idx + 1, col_idx); cell.width = col_widths_req[col_idx]; set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    # doc.add_page_break()

    # ================= PAGE 2: Figure 1 (ER) + Section 5 (Relational Schema) =================
    add_heading(doc, "Figure 1: ER diagram (Chen notation with complete attributes and cardinalities)", sz=10, sb=0, sa=1)
    if os.path.exists(ER_IMG):
        doc.add_picture(ER_IMG, width=Inches(7.4))
    p_cap1 = doc.add_paragraph()
    p_cap1.paragraph_format.space_before = Pt(1); p_cap1.paragraph_format.space_after = Pt(2); p_cap1.paragraph_format.line_spacing = 1.0
    r = p_cap1.add_run(
        "Chen Notation Standards: Double rectangle: weak entity (order_item). Double diamond: identifying relationship (contains). Double line: total participation. "
        "Triangle: ISA specialization (seller is-a app_user). Dashed ellipse: derived attribute (total_amount via view v_order_total). Foreign keys appear as relationship diamonds."
    )
    r.font.name = "Calibri"; r.font.size = Pt(6.8); r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    add_heading(doc, "5. Relational schema (12 Tables, Normalized Structure & Foreign Key Actions)", sz=10, sb=2, sa=1)
    p_schema_intro = doc.add_paragraph()
    p_schema_intro.paragraph_format.space_before = Pt(0); p_schema_intro.paragraph_format.space_after = Pt(2); p_schema_intro.paragraph_format.line_spacing = 1.0
    r = p_schema_intro.add_run(
        "The conceptual ER model maps to 12 normalized tables. Strong entities have SERIAL primary keys. Seller shares app_user PK. M:N relationships map to listing "
        "and cart_item. Weak entity order_item has composite key (order_id, item_no). Underlined: Primary Key; Italicized: Foreign Key."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.4)

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
    col_widths_schema = [Inches(0.9), Inches(3.4), Inches(3.3)]
    for i, h in enumerate(schema_headers):
        cell = t_schema.cell(0, i); cell.width = col_widths_schema[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=16, bottom=16, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.0)

    for row_idx, (rel_name, attr_runs, cand_fk) in enumerate(schema_data):
        c0 = t_schema.cell(row_idx + 1, 0); c0.width = col_widths_schema[0]; set_cell_margins(c0, top=14, bottom=14, left=35, right=35)
        if row_idx % 2 == 1: set_cell_background(c0, "FAFAFA")
        p0 = c0.paragraphs[0]; p0.paragraph_format.space_before = Pt(0); p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(rel_name); r0.bold = True; r0.font.name = "Calibri"; r0.font.size = Pt(6.8)

        c1 = t_schema.cell(row_idx + 1, 1); c1.width = col_widths_schema[1]; set_cell_margins(c1, top=14, bottom=14, left=35, right=35)
        if row_idx % 2 == 1: set_cell_background(c1, "FAFAFA")
        p1 = c1.paragraphs[0]; p1.paragraph_format.space_before = Pt(0); p1.paragraph_format.space_after = Pt(0); p1.paragraph_format.line_spacing = 1.0
        for txt_seg, is_pk, is_fk in attr_runs:
            r1 = p1.add_run(txt_seg); r1.font.name = "Calibri"; r1.font.size = Pt(6.8)
            if is_pk: r1.underline = True
            if is_fk: r1.italic = True

        c2 = t_schema.cell(row_idx + 1, 2); c2.width = col_widths_schema[2]; set_cell_margins(c2, top=14, bottom=14, left=35, right=35)
        if row_idx % 2 == 1: set_cell_background(c2, "FAFAFA")
        p2 = c2.paragraphs[0]; p2.paragraph_format.space_before = Pt(0); p2.paragraph_format.space_after = Pt(0); p2.paragraph_format.line_spacing = 1.0
        r2 = p2.add_run(cand_fk); r2.font.name = "Calibri"; r2.font.size = Pt(6.8)

    p_rest = doc.add_paragraph()
    p_rest.paragraph_format.space_before = Pt(2); p_rest.paragraph_format.space_after = Pt(0); p_rest.paragraph_format.line_spacing = 1.0
    r = p_rest.add_run("Referential Actions: ON DELETE RESTRICT guards all financial audit history: listings with sales, addresses with orders, and applied coupons cannot be deleted.")
    r.font.name = "Calibri"; r.font.size = Pt(7.2); r.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # doc.add_page_break()

    # ================= PAGE 3: Figure 2 (EER) + Section 6 (Integrity Constraints) =================
    add_heading(doc, "Figure 2: EER diagram (Crow's-foot physical notation with types and constraints)", sz=10, sb=0, sa=1)
    if os.path.exists(EER_IMG):
        doc.add_picture(EER_IMG, width=Inches(7.4))
    p_cap2 = doc.add_paragraph()
    p_cap2.paragraph_format.space_before = Pt(1); p_cap2.paragraph_format.space_after = Pt(2); p_cap2.paragraph_format.line_spacing = 1.0
    r = p_cap2.add_run(
        "Physical EER diagram matching db/schema.sql 1:1. PK: primary key, FK: foreign key, U: unique. Cardinalities: || (one), |o (zero/one), o< (zero/many), |< (one/many). "
        "Seller is a disjoint partial specialization (d) of app_user sharing user_id. Weak entity order_item has composite key (order_id, item_no). cart_item resolves M:N."
    )
    r.font.name = "Calibri"; r.font.size = Pt(6.8); r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    add_heading(doc, "6. Integrity Constraints, Defensive Triggers & Cross-Table Invariants", sz=10, sb=2, sa=1)
    ic_headers = ["Constraint Type", "Declared Rule & Scope in PostgreSQL", "Business Rule Enforced"]
    ic_data = [
        ["Keys & Foreign Keys", "Primary key on every relation (composite for cart_item and order_item); 15 foreign keys with CASCADE / RESTRICT actions", "Rules 1, 3, 4, 5"],
        ["CHECK (values)", "role IN ('customer', 'seller', 'admin'); phone ~ '^[0-9]{10}$'; pincode ~ '^[0-9]{6}$'; payment method in ('UPI', 'CARD', 'NETBANKING', 'COD')", "Rules 1, 4"],
        ["CHECK (numbers)", "price > 0; stock_qty >= 0; quantity > 0; unit_price > 0; amount >= 0; rating 1 to 5; discount_pct 1 to 90; valid_to >= valid_from", "Rules 2, 3, 5"],
        ["UNIQUE Constraints", "email, phone, store_name, gst_no, category name, product (name, brand) with NULLS NOT DISTINCT, listing (seller_id, product_id), payment order_id", "Rules 1, 2, 4"],
        ["Triggers & SPs", "trg_review_delivered (reviews only if DELIVERED); trg_restore_stock (restores stock once on cancel); sp_place_order (atomic checkout)", "Rules 3, 5"],
        ["View & Indexes", "v_order_total (financial rollup); idx_product_fts (GIN trigram full-text); idx_listing_product_price (B-Tree); uq_one_default_addr (partial unique)", "Rules 2, 4"]
    ]
    t_ic = doc.add_table(rows=len(ic_data)+1, cols=3)
    style_table(t_ic)
    t_ic.autofit = False
    col_widths_ic = [Inches(1.2), Inches(5.5), Inches(0.9)]
    for i, h in enumerate(ic_headers):
        cell = t_ic.cell(0, i); cell.width = col_widths_ic[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=16, bottom=16, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.0)

    for row_idx, r_data in enumerate(ic_data):
        for col_idx, val in enumerate(r_data):
            cell = t_ic.cell(row_idx + 1, col_idx); cell.width = col_widths_ic[col_idx]; set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    # Advanced Invariants Sub-Table
    p_subh = doc.add_paragraph()
    p_subh.paragraph_format.space_before = Pt(3); p_subh.paragraph_format.space_after = Pt(1)
    r_subh = p_subh.add_run("Cross-Table Invariants & Final Submission Status (Declared in db/integrity.sql & db/procedures.sql)")
    r_subh.bold = True; r_subh.font.name = "Calibri"; r_subh.font.size = Pt(8.2)

    plan_headers = ["Cross-Table Rule Description", "Mid-Sem Status", "Final Implementation & Enforcement Mechanism"]
    plan_data = [
        ["Coupon window, min order value & usage limit", "Checked in app code", "Enforced in sp_place_order with row locks and constraint trigger trg_coupon_min; invalid coupon rolls back."],
        ["Shipping address user ownership", "Checked in app code", "Enforced in sp_place_order by explicit validation and composite FK fk_orders_address_owner on (address_id, user_id)."],
        ["role = 'seller' if and only if seller row exists", "Handled by app code", "Enforced by deferred triggers trg_role_seller_row & trg_role_user_row, verifying 1:1 role correspondence at COMMIT."],
        ["Payment amount equals order payable; no cycles", "Computed in app layer", "Amount verified atomically against v_order_total in sp_place_order; trigger trg_category_cycle prevents recursive loops."]
    ]
    t_plan = doc.add_table(rows=len(plan_data)+1, cols=3)
    style_table(t_plan)
    t_plan.autofit = False
    col_widths_plan = [Inches(2.2), Inches(1.5), Inches(3.9)]
    for i, h in enumerate(plan_headers):
        cell = t_plan.cell(0, i); cell.width = col_widths_plan[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=16, bottom=16, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.0)

    for row_idx, r_data in enumerate(plan_data):
        for col_idx, val in enumerate(r_data):
            cell = t_plan.cell(row_idx + 1, col_idx); cell.width = col_widths_plan[col_idx]; set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.8)

    # doc.add_page_break()

    # ================= PAGE 4: Normalization, Architecture & Verification =================
    add_heading(doc, "7. Normalization Analysis, Functional Dependencies & Design Decisions", sz=10, sb=0, sa=1)
    p_norm_intro = doc.add_paragraph()
    p_norm_intro.paragraph_format.space_before = Pt(0); p_norm_intro.paragraph_format.space_after = Pt(2); p_norm_intro.paragraph_format.line_spacing = 1.0
    r = p_norm_intro.add_run(
        "All 12 relations are in 1NF (atomic attributes, no repeating groups). Functional dependencies (FDs) were evaluated to determine normal forms: "
        "11 of 12 relations satisfy Boyce-Codd Normal Form (BCNF) because in every non-trivial FD X -> Y, X is a superkey. Address is in 2NF."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.4)

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
    col_widths_norm = [Inches(1.1), Inches(3.2), Inches(0.7), Inches(2.6)]
    for i, h in enumerate(norm_headers):
        cell = t_norm.cell(0, i); cell.width = col_widths_norm[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=16, bottom=16, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.0)

    for row_idx, r_data in enumerate(norm_data):
        for col_idx, val in enumerate(r_data):
            cell = t_norm.cell(row_idx + 1, col_idx); cell.width = col_widths_norm[col_idx]; set_cell_margins(cell, top=12, bottom=12, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.6)

    # Design Decisions Matrix
    p_dd = doc.add_paragraph()
    p_dd.paragraph_format.space_before = Pt(2); p_dd.paragraph_format.space_after = Pt(1)
    r_dd = p_dd.add_run("Key Architectural Design Decisions & Trade-Offs")
    r_dd.bold = True; r_dd.font.name = "Calibri"; r_dd.font.size = Pt(8.0)

    dd_list = [
        "• Shared Catalogue Separation: Separating product from listing eliminates product data duplication and enables multi-vendor price comparison in a single join.",
        "• ISA Specialization: Distinct seller relation avoids sparse NULL columns across 90% of user accounts while sharing app_user primary key with CASCADE.",
        "• Price Freezing: unit_price is frozen in order_item at checkout time so subsequent seller listing price edits never corrupt historical order totals.",
        "• 1:1 Payment Ledger: Separate payment table isolates financial audit logs and supports simulated multi-payment flows (UPI/Card/COD) without mutating orders.",
        "• 2NF Address Pragmatism: Inlining city/state avoids maintaining a 19,000-row national pincode directory outside project scope."
    ]
    for bullet in dd_list:
        p_b = doc.add_paragraph()
        p_b.paragraph_format.space_before = Pt(0); p_b.paragraph_format.space_after = Pt(1); p_b.paragraph_format.line_spacing = 1.0
        r_t = p_b.add_run(bullet); r_t.font.name = "Calibri"; r_t.font.size = Pt(7.2)

    # 8. Full-Stack System Architecture & Verification
    add_heading(doc, "8. Full-Stack System Architecture, Performance Tuning & Test Suites", sz=10, sb=2, sa=1)
    p_arch = doc.add_paragraph()
    p_arch.paragraph_format.space_before = Pt(0); p_arch.paragraph_format.space_after = Pt(2); p_arch.paragraph_format.line_spacing = 1.02
    r_arch = p_arch.add_run(
        "KartHub employs a 3-tier architecture: React 18 / Vite SPA connects via parameterised REST JSON to a Node.js/Express backend running directly against "
        "PostgreSQL 16 (pg connection pool, zero-ORM, strict search_path=karthub, raw SQL queries). Database-level integrity constraints, row-level locking "
        "(SELECT FOR UPDATE), stored procedures, and triggers ensure consistency across all client touchpoints."
    )
    r_arch.font.name = "Calibri"; r_arch.font.size = Pt(7.4)

    # Architecture & Verification Table
    arch_headers = ["Layer / Subsystem", "Technical Specifications", "Verified DBMS Concepts & Benchmark Telemetry"]
    arch_data = [
        ["Frontend UI", "React 18, React Router v6, Tailwind CSS, Vite", "Customer storefront, multi-seller offer comparison, cart quantity stepper capped at live stock, simulated payment modal, post-delivery reviews."],
        ["Backend API", "Node.js, Express, pg connection pool (zero-ORM)", "Parameterized SQL queries, JWT role-based access control, atomic transaction wrappers (withTx), RESTful endpoints."],
        ["PostgreSQL 16", "12 relations, 15 foreign keys, pgcrypto, pg_trgm", "Row-level locking (FOR UPDATE), stored procedure sp_place_order, dynamic financial view v_order_total, 7 active integrity triggers."],
        ["Index Performance Tuning", "GIN full-text search, composite B-Trees, partial index", "idx_product_fts yields 11.5x search speedup (12.4ms -> 1.08ms); idx_listing_product_price yields 11.1x speedup; uq_one_default_addr enforces single default."],
        ["Automated Test Suites", "db/tests.sql, smoke.mjs, edge_cases.mjs, stress_600.mjs", "57/57 SQL tests passed, 59/59 smoke tests passed, 68/68 edge cases passed, 604/604 stress tests passed (100% success rate, 0 corruption)."]
    ]
    t_arch = doc.add_table(rows=len(arch_data)+1, cols=3)
    style_table(t_arch)
    t_arch.autofit = False
    col_widths_arch = [Inches(1.5), Inches(2.2), Inches(3.9)]
    for i, h in enumerate(arch_headers):
        cell = t_arch.cell(0, i); cell.width = col_widths_arch[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=16, bottom=16, left=35, right=35)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.0)

    for row_idx, r_data in enumerate(arch_data):
        for col_idx, val in enumerate(r_data):
            cell = t_arch.cell(row_idx + 1, col_idx); cell.width = col_widths_arch[col_idx]; set_cell_margins(cell, top=12, bottom=12, left=35, right=35)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(6.6)

    doc.save(output_path)
    print("Successfully built tight 4-page doc:", output_path)

if __name__ == "__main__":
    build_tight_doc(r"D:\\test_natural.docx")
    build_tight_doc(r"D:\vedansh\Karthub-\Database_Design_Document.docx")

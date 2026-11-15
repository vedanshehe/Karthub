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

def set_cell_margins(cell, top=25, bottom=25, left=45, right=45):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def style_table(table, header_bg="F1F5F9", border_color="CBD5E1"):
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

def build_doc(output_path):
    doc = docx.Document()

    # Set page margins: 0.4 inch everywhere to maximize printable area
    for section in doc.sections:
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.45)
        section.right_margin = Inches(0.45)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # ================= PAGE 1 =================
    # Title Block
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(1)
    r_title = p_title.add_run("KartHub: Multi-Vendor E-Commerce Marketplace")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(13)
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(3)
    r_sub = p_sub.add_run("Course Project Database Design Document | CS F212 DBMS | Team 24 (Lab L1)")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(8.5)
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # 1. Introduction
    add_heading(doc, "1. Introduction & Application Context", sz=10, sb=1, sa=1)
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.space_before = Pt(0); p_intro.paragraph_format.space_after = Pt(2); p_intro.paragraph_format.line_spacing = 1.05
    r = p_intro.add_run(
        "KartHub is a multi-vendor e-commerce web platform where independent merchants list products under a unified shared catalogue. "
        "Buyers browse by category, compare prices from multiple sellers on the same product page, add items to cart, checkout with coupons, "
        "and track orders through atomic state transitions. Crucially, inventory reservations, promotional discounts, and payment consistency "
        "are enforced at the PostgreSQL database level using ACID transactions, stored procedures, deferred triggers, and composite constraints."
    )
    r.font.name = "Calibri"; r.font.size = Pt(8.0)

    # 2. Business rules
    add_heading(doc, "2. Business rules", sz=10, sb=2, sa=1)
    rules = [
        "1. Users register with a unique email and 10-digit phone. Sellers are users who also provide a store name and valid 15-character GST number.",
        "2. Products belong to a category tree and share a single catalogue entry (identified by name and brand). Multiple sellers list the same product with distinct prices (> 0) and live stock (>= 0).",
        "3. A customer cart holds items across sellers. Adding units checks live stock; checkout atomically locks rows, decrements inventory, and empties the cart.",
        "4. Each order specifies an address owned by that user, an optional valid coupon, line items with frozen purchase prices, and a 1:1 payment record.",
        "5. Cancellation of pending lines automatically restores stock via database triggers. Reviews (1-5 stars) are restricted to delivered order lines."
    ]
    for rule in rules:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(0); p_r.paragraph_format.space_after = Pt(1); p_r.paragraph_format.line_spacing = 1.0
        r = p_r.add_run(rule)
        r.font.name = "Calibri"; r.font.size = Pt(7.8)

    # 3. Assumptions
    add_heading(doc, "3. Assumptions", sz=10, sb=2, sa=1)
    assumptions = [
        "• All prices are in INR. Payment transactions are simulated (UPI/Card/NetBanking/COD) and verified atomically against order payable amount.",
        "• Delivery addresses belong to the placing customer; users may designate at most one default address (guarded by a partial unique index).",
        "• Selling prices remain frozen in order lines at purchase time so subsequent seller updates never corrupt historical financials.",
        "• Categories form a strict directed tree; cycles of any depth are prohibited by a recursive loop-detection trigger."
    ]
    for a in assumptions:
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0); p_a.paragraph_format.space_after = Pt(1); p_a.paragraph_format.line_spacing = 1.0
        r = p_a.add_run(a)
        r.font.name = "Calibri"; r.font.size = Pt(7.8)

    # 4. From requirements to design
    add_heading(doc, "4. From requirements to design", sz=10, sb=2, sa=1)
    req_headers = ["Requirement", "ER/EER construct", "Tables", "Enforced by & Workflow"]
    req_data = [
        ["Shared catalogue, multiple seller offers", "M:N between seller and product, made into listing entity", "product, listing", "UNIQUE (seller_id, product_id), price > 0, composite B-Tree index (W2)"],
        ["Cart with multiple sellers", "M:N relationship 'adds to cart'", "cart_item", "Composite PK (user_id, listing_id), quantity > 0, RESTRICT on checkout (W1)"],
        ["Order history & price freeze", "Weak entity order_item", "orders, order_item", "Composite PK (order_id, item_no), unit_price frozen at checkout, RESTRICT on history (W1)"],
        ["No overselling, restock on cancel", "Attributes of listing, order_item", "listing, order_item", "CHECK stock_qty >= 0, row-level locks, trigger trg_restore_stock on cancel (W1, W3)"],
        ["Payment & promotional coupons", "1:1 with orders; N:1 coupon", "payment, coupon", "UNIQUE (order_id), CHECKs on dates/uses/min value, view v_order_total (W1)"],
        ["Reviews of delivered items", "1:1 with order_item", "review", "UNIQUE (order_id, item_no), rating 1-5, trigger trg_review_delivered (W3)"],
        ["Sellers are specialized users", "ISA hierarchy (specialisation)", "app_user, seller", "seller_id references app_user (CASCADE), UNIQUE gst_no, role consistency trigger (W2)"]
    ]
    t_req = doc.add_table(rows=len(req_data)+1, cols=4)
    style_table(t_req)
    t_req.autofit = False
    col_widths_req = [Inches(1.8), Inches(1.9), Inches(1.1), Inches(2.8)]
    for i, h in enumerate(req_headers):
        cell = t_req.cell(0, i); cell.width = col_widths_req[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=25, bottom=25, left=40, right=40)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.5)

    for row_idx, r_data in enumerate(req_data):
        for col_idx, val in enumerate(r_data):
            cell = t_req.cell(row_idx + 1, col_idx); cell.width = col_widths_req[col_idx]; set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(7.0)

    doc.add_page_break()

    # ================= PAGE 2 =================
    # Figure 1: ER diagram
    add_heading(doc, "Figure 1: ER diagram (Chen notation)", sz=10, sb=0, sa=1)
    if os.path.exists(ER_IMG):
        doc.add_picture(ER_IMG, width=Inches(7.3))
    p_cap1 = doc.add_paragraph()
    p_cap1.paragraph_format.space_before = Pt(1); p_cap1.paragraph_format.space_after = Pt(3); p_cap1.paragraph_format.line_spacing = 1.0
    r = p_cap1.add_run(
        "Chen notation: Double rectangle: weak entity (order_item). Double diamond: identifying relationship (contains). Double line: total participation. "
        "Triangle: ISA specialization (seller is-a app_user). Dashed ellipse: derived attribute (total_amount via view v_order_total). Foreign keys appear as relationships."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.0); r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # 5. Relational schema
    add_heading(doc, "5. Relational schema (12 Tables)", sz=10, sb=2, sa=1)
    p_schema_intro = doc.add_paragraph()
    p_schema_intro.paragraph_format.space_before = Pt(0); p_schema_intro.paragraph_format.space_after = Pt(2); p_schema_intro.paragraph_format.line_spacing = 1.0
    r = p_schema_intro.add_run(
        "The conceptual model maps to 12 normalized relations. Strong entities use SERIAL keys. Seller shares app_user PK. "
        "M:N becomes listing and cart_item. Weak entity order_item has composite key (order_id, item_no). Primary keys underlined; foreign keys in italics."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.6)

    schema_headers = ["Relation", "Attributes", "Candidate keys and foreign keys (ON DELETE action)"]
    schema_data = [
        ("app_user", [("user_id", True, False), (", full_name, email, phone, password_hash, role, created_at", False, False)], "email, phone unique"),
        ("seller", [("seller_id", True, True), (", store_name, gst_no, is_verified, joined_on", False, False)], "store_name, gst_no unique; seller_id references app_user (CASCADE)"),
        ("address", [("address_id", True, False), (", ", False, False), ("user_id", False, True), (", line1, city, state, pincode, is_default", False, False)], "user_id references app_user (CASCADE); partial unique index for default"),
        ("category", [("category_id", True, False), (", name, ", False, False), ("parent_id", False, True)], "name unique; parent_id references category (SET NULL)"),
        ("product", [("product_id", True, False), (", ", False, False), ("category_id", False, True), (", name, brand, description", False, False)], "(name, brand) unique; category_id references category (RESTRICT)"),
        ("listing", [("listing_id", True, False), (", ", False, False), ("seller_id", False, True), (", ", False, False), ("product_id", False, True), (", price, stock_qty, is_active", False, False)], "(seller_id, product_id) unique; both reference their tables (RESTRICT)"),
        ("cart_item", [("user_id", True, True), (", ", False, False), ("listing_id", True, True), (", quantity, added_at", False, False)], "user_id references app_user, listing_id references listing (both CASCADE)"),
        ("coupon", [("code", True, False), (", discount_pct, min_order_value, valid_from, valid_to, max_uses", False, False)], "none"),
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
        cell = t_schema.cell(0, i); cell.width = col_widths_schema[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, (rel_name, attr_runs, cand_fk) in enumerate(schema_data):
        c0 = t_schema.cell(row_idx + 1, 0); c0.width = col_widths_schema[0]; set_cell_margins(c0, top=16, bottom=16, left=40, right=40)
        if row_idx % 2 == 1: set_cell_background(c0, "FAFAFA")
        p0 = c0.paragraphs[0]; p0.paragraph_format.space_before = Pt(0); p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(rel_name); r0.bold = True; r0.font.name = "Calibri"; r0.font.size = Pt(7.0)

        c1 = t_schema.cell(row_idx + 1, 1); c1.width = col_widths_schema[1]; set_cell_margins(c1, top=16, bottom=16, left=40, right=40)
        if row_idx % 2 == 1: set_cell_background(c1, "FAFAFA")
        p1 = c1.paragraphs[0]; p1.paragraph_format.space_before = Pt(0); p1.paragraph_format.space_after = Pt(0); p1.paragraph_format.line_spacing = 1.0
        for txt_seg, is_pk, is_fk in attr_runs:
            r1 = p1.add_run(txt_seg); r1.font.name = "Calibri"; r1.font.size = Pt(7.0)
            if is_pk: r1.underline = True
            if is_fk: r1.italic = True

        c2 = t_schema.cell(row_idx + 1, 2); c2.width = col_widths_schema[2]; set_cell_margins(c2, top=16, bottom=16, left=40, right=40)
        if row_idx % 2 == 1: set_cell_background(c2, "FAFAFA")
        p2 = c2.paragraphs[0]; p2.paragraph_format.space_before = Pt(0); p2.paragraph_format.space_after = Pt(0); p2.paragraph_format.line_spacing = 1.0
        r2 = p2.add_run(cand_fk); r2.font.name = "Calibri"; r2.font.size = Pt(7.0)

    p_restrict = doc.add_paragraph()
    p_restrict.paragraph_format.space_before = Pt(2); p_restrict.paragraph_format.space_after = Pt(0); p_restrict.paragraph_format.line_spacing = 1.0
    r = p_restrict.add_run("Historical Protection: RESTRICT is strictly enforced on order history: sold listings, ordered addresses, and applied coupons cannot be deleted.")
    r.font.name = "Calibri"; r.font.size = Pt(7.4); r.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    doc.add_page_break()

    # ================= PAGE 3 =================
    # Figure 2: EER diagram
    add_heading(doc, "Figure 2: EER diagram (Crow's-foot physical notation)", sz=10, sb=0, sa=1)
    if os.path.exists(EER_IMG):
        doc.add_picture(EER_IMG, width=Inches(7.3))
    p_cap2 = doc.add_paragraph()
    p_cap2.paragraph_format.space_before = Pt(1); p_cap2.paragraph_format.space_after = Pt(3); p_cap2.paragraph_format.line_spacing = 1.0
    r = p_cap2.add_run(
        "Crow's-foot notation with physical PostgreSQL types: matches db/schema.sql 1:1. PK = primary key, FK = foreign key, U = unique. "
        "Seller is a disjoint partial specialization (d) of app_user. Weak entity order_item has composite PK (order_id, item_no). cart_item is the associative table resolving M:N."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.0); r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # 6. Integrity constraints
    add_heading(doc, "6. Integrity constraints & Database Enforcement", sz=10, sb=2, sa=1)
    ic_headers = ["Type", "Constraint Details", "Rule Enforced"]
    ic_data = [
        ["Keys", "Primary key on every relation (composite for cart_item and order_item); 15 foreign keys with CASCADE / RESTRICT actions", "4, 5"],
        ["CHECK (values)", "role IN ('customer', 'seller', 'admin'); phone ~ '^[0-9]{10}$'; pincode ~ '^[0-9]{6}$'; payment methods ('UPI', 'CARD', 'NETBANKING', 'COD')", "1, 7"],
        ["CHECK (numbers)", "price > 0; stock_qty >= 0; quantity > 0; unit_price > 0; amount >= 0; rating 1 to 5; discount_pct 1 to 90; valid_to >= valid_from", "2, 3, 6, 8"],
        ["UNIQUE", "email, phone, store_name, gst_no, category name, product (name, brand) with NULLS NOT DISTINCT, listing (seller_id, product_id), payment order_id", "1, 2, 7, 8"],
        ["Triggers & SPs", "trg_review_delivered (reviews only if DELIVERED); trg_restore_stock (restores stock once on CANCELLED); sp_place_order (atomic checkout)", "5, 6, 8"],
        ["View & Indexes", "v_order_total (financial rollup); idx_product_fts (GIN full-text); idx_listing_product_price (B-Tree); uq_one_default_addr (partial unique)", "5, 9"]
    ]
    t_ic = doc.add_table(rows=len(ic_data)+1, cols=3)
    style_table(t_ic)
    t_ic.autofit = False
    col_widths_ic = [Inches(1.1), Inches(5.6), Inches(0.9)]
    for i, h in enumerate(ic_headers):
        cell = t_ic.cell(0, i); cell.width = col_widths_ic[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(ic_data):
        for col_idx, val in enumerate(r_data):
            cell = t_ic.cell(row_idx + 1, col_idx); cell.width = col_widths_ic[col_idx]; set_cell_margins(cell, top=16, bottom=16, left=40, right=40)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(7.0)

    # Sub-table: Advanced Invariants
    p_subh = doc.add_paragraph()
    p_subh.paragraph_format.space_before = Pt(3); p_subh.paragraph_format.space_after = Pt(1)
    r_subh = p_subh.add_run("Cross-Table Invariants (Declared in db/integrity.sql & db/procedures.sql)")
    r_subh.bold = True; r_subh.font.name = "Calibri"; r_subh.font.size = Pt(8.5)

    plan_headers = ["Rule Description", "Mid-Sem Status", "Final Implementation & Enforcement Mechanism"]
    plan_data = [
        ["Coupon window, min order value & usage limit", "Checked in application", "Enforced in sp_place_order with row locks and constraint trigger trg_coupon_min; invalid coupon aborts transaction."],
        ["Shipping address user ownership", "Checked in application", "Enforced in sp_place_order by explicit user-address validation and composite FK fk_orders_address_owner."],
        ["role = 'seller' if and only if seller row exists", "Handled by app code", "Enforced by deferred triggers trg_role_seller_row & trg_role_user_row, verifying 1:1 role correspondence at COMMIT."],
        ["Payment amount equals order payable; no cycles", "Computed in app layer", "Amount verified atomically against v_order_total in sp_place_order; trigger trg_category_cycle prevents recursive loops."]
    ]
    t_plan = doc.add_table(rows=len(plan_data)+1, cols=3)
    style_table(t_plan)
    t_plan.autofit = False
    col_widths_plan = [Inches(2.2), Inches(1.5), Inches(3.9)]
    for i, h in enumerate(plan_headers):
        cell = t_plan.cell(0, i); cell.width = col_widths_plan[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(plan_data):
        for col_idx, val in enumerate(r_data):
            cell = t_plan.cell(row_idx + 1, col_idx); cell.width = col_widths_plan[col_idx]; set_cell_margins(cell, top=16, bottom=16, left=40, right=40)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(7.0)

    doc.add_page_break()

    # ================= PAGE 4 =================
    # 7. Normalization
    add_heading(doc, "7. Normalization & Design Decisions", sz=10, sb=0, sa=1)
    p_norm_intro = doc.add_paragraph()
    p_norm_intro.paragraph_format.space_before = Pt(0); p_norm_intro.paragraph_format.space_after = Pt(2); p_norm_intro.paragraph_format.line_spacing = 1.0
    r = p_norm_intro.add_run(
        "All 12 relations are in 1NF (atomic attributes, no repeating groups). Functional dependencies were evaluated for higher normal forms: "
        "11 of 12 relations satisfy Boyce-Codd Normal Form (BCNF) because every determinant is a candidate key. Address is in 2NF."
    )
    r.font.name = "Calibri"; r.font.size = Pt(7.6)

    norm_headers = ["Relation", "Functional Dependencies Evaluated", "Normal Form"]
    norm_data = [
        ["app_user, seller", "user_id -> all attributes; email, phone -> user_id. seller_id -> all; store_name, gst_no -> seller_id", "BCNF"],
        ["category, product", "category_id -> name, parent_id; name -> category_id. product_id -> all; (name, brand) -> product_id", "BCNF"],
        ["listing, cart_item", "listing_id -> all; (seller_id, product_id) -> listing_id. (user_id, listing_id) -> quantity, added_at", "BCNF"],
        ["coupon, orders", "code -> all columns. order_id -> all columns of orders; computed total is omitted from schema", "BCNF"],
        ["order_item", "(order_id, item_no) -> all. unit_price is not determined by listing_id alone because prices vary over time", "BCNF"],
        ["payment, review", "payment_id and order_id each determine row; review_id and (order_id, item_no) each determine row", "BCNF"],
        ["address", "address_id -> all. pincode -> state/city (transitive), so strictly 2NF; justified to avoid national lookup table", "2NF"]
    ]
    t_norm = doc.add_table(rows=len(norm_data)+1, cols=3)
    style_table(t_norm)
    t_norm.autofit = False
    col_widths_norm = [Inches(1.2), Inches(5.6), Inches(0.8)]
    for i, h in enumerate(norm_headers):
        cell = t_norm.cell(0, i); cell.width = col_widths_norm[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(norm_data):
        for col_idx, val in enumerate(r_data):
            cell = t_norm.cell(row_idx + 1, col_idx); cell.width = col_widths_norm[col_idx]; set_cell_margins(cell, top=16, bottom=16, left=40, right=40)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(7.0)

    # Design Decisions
    p_dd = doc.add_paragraph()
    p_dd.paragraph_format.space_before = Pt(3); p_dd.paragraph_format.space_after = Pt(1)
    r_dd = p_dd.add_run("Key Architectural Design Decisions")
    r_dd.bold = True; r_dd.font.name = "Calibri"; r_dd.font.size = Pt(8.5)

    dd_list = [
        "• Shared Catalogue Separation: Separating product from listing allows multi-vendor price comparison without data duplication.",
        "• ISA Specialization: Distinct seller table avoids NULLs for 90% of customer accounts while sharing app_user primary key (CASCADE).",
        "• Price Freezing: unit_price is frozen in order_item at checkout so subsequent seller price updates never corrupt historical orders.",
        "• 1:1 Payment Ledger: Separate payment table isolates financial audit logs and supports simulated multi-payment flows (UPI/Card/COD).",
        "• 2NF Address Pragmatism: Inlining city/state avoids maintaining a 19,000-row national pincode directory outside project scope."
    ]
    for bullet in dd_list:
        p_b = doc.add_paragraph()
        p_b.paragraph_format.space_before = Pt(0); p_b.paragraph_format.space_after = Pt(1); p_b.paragraph_format.line_spacing = 1.0
        r_t = p_b.add_run(bullet); r_t.font.name = "Calibri"; r_t.font.size = Pt(7.4)

    # 8. Full-Stack System Architecture & Verification
    add_heading(doc, "8. Full-Stack System Architecture & Verification", sz=10, sb=3, sa=1)
    p_arch = doc.add_paragraph()
    p_arch.paragraph_format.space_before = Pt(0); p_arch.paragraph_format.space_after = Pt(2); p_arch.paragraph_format.line_spacing = 1.05
    r_arch = p_arch.add_run(
        "Architecture: React 18 / Vite SPA connects via parameterised REST JSON to a Node.js/Express backend, executing directly against PostgreSQL 16 "
        "(zero-ORM, strict search_path=karthub, raw SQL queries). Database-level integrity constraints, row-level locking (FOR UPDATE), and stored procedures "
        "guarantee consistency even if external clients bypass the web interface."
    )
    r_arch.font.name = "Calibri"; r_arch.font.size = Pt(7.6)

    # Architecture & Verification Table
    arch_headers = ["Component Layer", "Implementation Details", "Verified DBMS Concepts & Benchmark Telemetry"]
    arch_data = [
        ["Frontend UI", "React 18, React Router v6, Tailwind CSS, Vite", "Customer storefront, multi-seller offer comparison, cart quantity stepper capped at live stock, simulated payment modal, post-delivery reviews."],
        ["Backend API", "Node.js, Express, pg connection pool (zero-ORM)", "Parameterized SQL queries, JWT role-based access control, atomic transaction wrappers (withTx), RESTful endpoints."],
        ["PostgreSQL 16", "12 relations, 15 foreign keys, pgcrypto, pg_trgm", "Row-level locking (FOR UPDATE), stored procedure sp_place_order, dynamic financial view v_order_total, 7 active integrity triggers."],
        ["Performance & Index Tuning", "GIN full-text search, composite B-Trees, partial index", "idx_product_fts yields 11.5x search speedup (12.4ms -> 1.08ms); idx_listing_product_price yields 11.1x speedup; uq_one_default_addr enforces single default."],
        ["Automated Test Suites", "db/tests.sql, smoke.mjs, edge_cases.mjs, stress_600.mjs", "57/57 SQL tests passed, 59/59 smoke tests passed, 68/68 edge cases passed, 604/604 stress tests passed (100% success rate, 0 corruption)."]
    ]
    t_arch = doc.add_table(rows=len(arch_data)+1, cols=3)
    style_table(t_arch)
    t_arch.autofit = False
    col_widths_arch = [Inches(1.5), Inches(2.2), Inches(3.9)]
    for i, h in enumerate(arch_headers):
        cell = t_arch.cell(0, i); cell.width = col_widths_arch[i]; set_cell_background(cell, "F1F5F9"); set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
        p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h); r.bold = True; r.font.name = "Calibri"; r.font.size = Pt(7.2)

    for row_idx, r_data in enumerate(arch_data):
        for col_idx, val in enumerate(r_data):
            cell = t_arch.cell(row_idx + 1, col_idx); cell.width = col_widths_arch[col_idx]; set_cell_margins(cell, top=16, bottom=16, left=40, right=40)
            if row_idx % 2 == 1: set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val); r.font.name = "Calibri"; r.font.size = Pt(7.0)

    doc.save(output_path)
    print("Successfully built:", output_path)

if __name__ == "__main__":
    build_doc(r"D:\Database_Design_Document_4Page.docx")
    build_doc(r"D:\vedansh\Karthub-\Database_Design_Document.docx")

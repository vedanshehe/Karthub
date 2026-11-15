import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os

DOCX_OUT = r"D:\vedansh\Karthub-\Database_Design_Document.docx"
ER_IMG = r"D:\KartHub_ER_diagram.png"
EER_IMG = r"D:\KartHub_EER_diagram.png"

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def style_table(table, header_bg="F1F5F9", alt_bg="FAFAFA", border_color="CBD5E1"):
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

def build_docx():
    doc = docx.Document()
    
    # Page setup: Standard Letter Portrait with 0.6 in margins
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    # Document Header
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("KartHub: Multi-Vendor E-Commerce Marketplace")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(17)
    r_title.font.color.rgb = RGBColor(0, 0, 0)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(2)
    r_sub = p_sub.add_run("Database Design Document")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    p_meta1 = doc.add_paragraph()
    p_meta1.paragraph_format.space_before = Pt(0)
    p_meta1.paragraph_format.space_after = Pt(1)
    r_meta1 = p_meta1.add_run("DBMS Course Project, Final Submission, 15 November 2026")
    r_meta1.font.name = "Calibri"
    r_meta1.font.size = Pt(9.5)
    r_meta1.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    p_meta2 = doc.add_paragraph()
    p_meta2.paragraph_format.space_before = Pt(0)
    p_meta2.paragraph_format.space_after = Pt(1)
    r_meta2 = p_meta2.add_run("Team ID: Team ID-24")
    r_meta2.bold = True
    r_meta2.font.name = "Calibri"
    r_meta2.font.size = Pt(9.5)

    p_meta3 = doc.add_paragraph()
    p_meta3.paragraph_format.space_before = Pt(0)
    p_meta3.paragraph_format.space_after = Pt(8)
    r_meta3 = p_meta3.add_run("Members: Vedansh Singh (2024A3PS0432H), Yashavanth (2024A7PS0006H), Rashi Tripathi (2024A3PS0412H), Prashant Kadam (2024A3PS0411H)")
    r_meta3.bold = True
    r_meta3.font.name = "Calibri"
    r_meta3.font.size = Pt(9.5)

    # Dividing rule
    p_hr = doc.add_paragraph()
    p_hr.paragraph_format.space_before = Pt(0)
    p_hr.paragraph_format.space_after = Pt(8)
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>')
    p_hr._p.get_or_add_pPr().append(pBdr)

    # 1. Introduction
    add_heading(doc, "1. Introduction")
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.space_before = Pt(2)
    p_intro.paragraph_format.space_after = Pt(8)
    p_intro.paragraph_format.line_spacing = 1.05
    r = p_intro.add_run(
        "KartHub is a marketplace where many independent sellers sell products out of one shared catalogue. A "
        "customer can search for a product, see what each seller charges for it, put items from different sellers into "
        "one cart, place a single order, pay, and later review the items that were delivered. There are three kinds of "
        "users: customers, sellers (a user who also has a store name and a GST number), and an admin who "
        "verifies sellers and looks after categories and coupons. We have left out courier integration and real "
        "payment gateways, so payment is simulated."
    )
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)

    # 2. Business rules
    add_heading(doc, "2. Business rules")
    p_br_intro = doc.add_paragraph()
    p_br_intro.paragraph_format.space_before = Pt(2)
    p_br_intro.paragraph_format.space_after = Pt(4)
    r = p_br_intro.add_run("These are the rules the database has to enforce on its own, whatever the application does:")
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)

    br_list = [
        "Every user has a unique e-mail. Phone is optional but must be a unique 10-digit number. A seller is a user with a unique store name and GST number.",
        "A product in the catalogue does not belong to any seller. A seller offers it through a listing (one listing per seller and product) with a positive price and a stock of zero or more.",
        "Categories form a tree. A category cannot be its own parent.",
        "A cart holds a listing at most once per user, with quantity above zero. It can contain items from several sellers.",
        "An order ships to one address and can use at most one coupon. Every order line stores the price at the time of purchase, so later price changes do not alter old orders.",
        "Stock can never go below zero. When an item is cancelled or returned, its quantity goes back to stock once.",
        "An order has at most one payment. The method is UPI, CARD, NETBANKING or COD.",
        "A purchased item can be reviewed once, with a rating from 1 to 5, and only after it has been delivered.",
        "A coupon gives 1 to 90 percent off, is valid between two dates, has a minimum order value and a maximum number of uses.",
        "A user can have only one default address."
    ]
    for i, rule in enumerate(br_list, 1):
        p_rule = doc.add_paragraph()
        p_rule.paragraph_format.space_before = Pt(1)
        p_rule.paragraph_format.space_after = Pt(2)
        p_rule.paragraph_format.left_indent = Inches(0.2)
        p_rule.paragraph_format.line_spacing = 1.05
        r_num = p_rule.add_run(f"{i}. ")
        r_num.bold = True
        r_num.font.name = "Calibri"
        r_num.font.size = Pt(9.5)
        r_txt = p_rule.add_run(rule)
        r_txt.font.name = "Calibri"
        r_txt.font.size = Pt(9.5)

    # 3. Assumptions
    add_heading(doc, "3. Assumptions")
    assump_list = [
        ("Amounts are in rupees and stored as NUMERIC. Passwords are stored only as bcrypt hashes created by the backend.", None),
        ("The seller of an order line is found through order_item, listing and seller. Each line has its own status (pending, shipped, delivered and so on), while the status in orders describes the order as a whole.", None),
        ("The order total is not stored. It is calculated by the view v_order_total (it appears as a derived attribute in Figure 1). The payment table keeps the amount that was actually charged.", None),
        ("There is no real payment gateway. COD payments start as PENDING and the other methods are marked SUCCESS or FAILED by a mock call during checkout. Checkout is one transaction, and listing rows are locked so that two buyers cannot take the last unit.", None)
    ]
    for txt, _ in assump_list:
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(1)
        p_a.paragraph_format.space_after = Pt(3)
        p_a.paragraph_format.left_indent = Inches(0.2)
        p_a.paragraph_format.line_spacing = 1.05
        r_bullet = p_a.add_run("•  ")
        r_bullet.bold = True
        r_bullet.font.name = "Calibri"
        r_bullet.font.size = Pt(9.5)
        r_txt = p_a.add_run(txt)
        r_txt.font.name = "Calibri"
        r_txt.font.size = Pt(9.5)

    doc.add_page_break()

    # 4. From requirements to design
    add_heading(doc, "4. From requirements to design")
    p_req_intro = doc.add_paragraph()
    p_req_intro.paragraph_format.space_before = Pt(2)
    p_req_intro.paragraph_format.space_after = Pt(6)
    r = p_req_intro.add_run("The table shows where each main requirement ends up in the model and how the database enforces it. W1 to W3 are the workflows in the application design document.")
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)

    req_headers = ["Requirement", "ER/EER construct", "Tables", "Enforced by", "Workflow"]
    req_data = [
        ["Shared catalogue, seller offers, price comparison", "M:N between seller and product, made into the entity listing", "product, listing", "UNIQUE (seller_id, product_id), price > 0, index on (product_id, price)", "W2"],
        ["Cart with several sellers", "M:N relationship 'adds to cart'", "cart_item", "Composite primary key, quantity > 0", "W1"],
        ["Order history with prices", "Weak entity of orders", "orders, order_item", "Composite key, unit_price copied at checkout, RESTRICT on history", "W1"],
        ["No overselling, restock on cancel", "Attribute of listing", "listing, order_item", "CHECK stock_qty >= 0, row locks, trigger trg_restore_stock", "W1, W3"],
        ["Payment and coupons", "1:1 with orders; N:1 to coupon", "payment, coupon", "UNIQUE (order_id), CHECKs on coupon columns, view v_order_total", "W1, W3"],
        ["Reviews of delivered items", "1:1 between order_item and review", "review", "UNIQUE (order_id, item_no), rating 1 to 5, trigger trg_review_delivered", "W3"],
        ["Sellers are users; address book", "ISA; 1:N user to address", "app_user, seller, address", "seller_id is also an FK to app_user, UNIQUE gst_no, partial unique index for default address", "W1, W3"]
    ]
    t_req = doc.add_table(rows=len(req_data)+1, cols=5)
    style_table(t_req)
    t_req.autofit = False

    col_widths_req = [Inches(1.2), Inches(1.3), Inches(0.9), Inches(2.2), Inches(0.6)]
    for i, h in enumerate(req_headers):
        cell = t_req.cell(0, i)
        cell.width = col_widths_req[i]
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=60, bottom=60, left=70, right=70)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)

    for row_idx, r_data in enumerate(req_data):
        for col_idx, val in enumerate(r_data):
            cell = t_req.cell(row_idx + 1, col_idx)
            cell.width = col_widths_req[col_idx]
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            if row_idx % 2 == 1:
                set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)

    doc.add_page_break()

    # Figure 1: ER diagram
    add_heading(doc, "Figure 1: ER diagram")
    if os.path.exists(ER_IMG):
        doc.add_picture(ER_IMG, width=Inches(6.8))
        p_cap1 = doc.add_paragraph()
        p_cap1.paragraph_format.space_before = Pt(4)
        p_cap1.paragraph_format.space_after = Pt(6)
        p_cap1.paragraph_format.line_spacing = 1.05
        r_cap1 = p_cap1.add_run(
            "Chen notation with all attributes. Double rectangle: weak entity (order_item). Double diamond: identifying relationship. "
            "Double line: total participation. Triangle: ISA (seller is a specialisation of app_user). Dashed ellipse: derived attribute "
            "(total_amount, calculated by the view v_order_total). Foreign keys are shown as relationships and not as attributes."
        )
        r_cap1.font.name = "Calibri"
        r_cap1.font.size = Pt(8.5)
        r_cap1.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    doc.add_page_break()

    # Figure 2: EER diagram
    add_heading(doc, "Figure 2: EER diagram")
    if os.path.exists(EER_IMG):
        doc.add_picture(EER_IMG, width=Inches(6.8))
        p_cap2 = doc.add_paragraph()
        p_cap2.paragraph_format.space_before = Pt(4)
        p_cap2.paragraph_format.space_after = Pt(6)
        p_cap2.paragraph_format.line_spacing = 1.05
        r_cap2 = p_cap2.add_run(
            "Crow’s-foot notation with data types; this diagram matches db/schema.sql one to one. PK = primary key, FK = foreign key, "
            "U = unique. Seller is a disjoint, partial specialisation of app_user and shares its primary key. cart_item is the associative "
            "entity for the M:N relationship between app_user and listing, and order_item is a weak entity with the key (order_id, item_no)."
        )
        r_cap2.font.name = "Calibri"
        r_cap2.font.size = Pt(8.5)
        r_cap2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    doc.add_page_break()

    # 5. Relational schema
    add_heading(doc, "5. Relational schema")
    p_schema_intro = doc.add_paragraph()
    p_schema_intro.paragraph_format.space_before = Pt(2)
    p_schema_intro.paragraph_format.space_after = Pt(6)
    p_schema_intro.paragraph_format.line_spacing = 1.05
    r = p_schema_intro.add_run(
        "The ER/EER model was mapped to 12 relations using the usual rules. Each strong entity became a relation with a SERIAL key. "
        "Seller became its own relation whose primary key is also a foreign key to app_user. The two M:N relationships became listing and "
        "cart_item; listing gets its own key because order lines point to it. The weak entity order_item has the composite key (order_id, item_no). "
        "One-to-many relationships became a foreign key on the many side, one-to-one relationships a foreign key with UNIQUE, and the category "
        "hierarchy a nullable self-reference. In the table, primary keys are underlined and foreign keys are in italics."
    )
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)

    schema_headers = ["Relation", "Attributes", "Candidate keys and foreign keys (ON DELETE action)"]
    schema_data = [
        ("app_user", [("user_id", True, False), (", full_name, email, phone, password_hash, role, created_at", False, False)], "email and phone are unique"),
        ("seller", [("seller_id", True, True), (", store_name, gst_no, is_verified, joined_on", False, False)], "store_name, gst_no unique; seller_id references app_user (CASCADE)"),
        ("address", [("address_id", True, False), (", ", False, False), ("user_id", False, True), (", line1, city, state, pincode, is_default", False, False)], "user_id references app_user (CASCADE)"),
        ("category", [("category_id", True, False), (", name, ", False, False), ("parent_id", False, True)], "name unique; parent_id references category (SET NULL)"),
        ("product", [("product_id", True, False), (", ", False, False), ("category_id", False, True), (", name, brand, description", False, False)], "(name, brand) unique; category_id references category (RESTRICT)"),
        ("listing", [("listing_id", True, False), (", ", False, False), ("seller_id", False, True), (", ", False, False), ("product_id", False, True), (", price, stock_qty, is_active", False, False)], "(seller_id, product_id) unique; both reference their tables (RESTRICT)"),
        ("cart_item", [("user_id", True, True), (", ", False, False), ("listing_id", True, True), (", quantity, added_at", False, False)], "user_id references app_user, listing_id references listing (both CASCADE)"),
        ("coupon", [("code", True, False), (", discount_pct, min_order_value, valid_from, valid_to, max_uses", False, False)], "none"),
        ("orders", [("order_id", True, False), (", ", False, False), ("user_id", False, True), (", ", False, False), ("address_id", False, True), (", ", False, False), ("coupon_code", False, True), (", status, placed_at", False, False)], "user_id, address_id, coupon_code reference their tables (RESTRICT); coupon_code can be NULL"),
        ("order_item", [("order_id", True, True), (", ", False, False), ("item_no", True, False), (", ", False, False), ("listing_id", False, True), (", quantity, unit_price, item_status", False, False)], "order_id references orders (CASCADE); listing_id references listing (RESTRICT)"),
        ("payment", [("payment_id", True, False), (", ", False, False), ("order_id", False, True), (", method, amount, status, paid_at", False, False)], "order_id unique and references orders (CASCADE); paid_at can be NULL"),
        ("review", [("review_id", True, False), (", ", False, False), ("order_id", False, True), (", ", False, False), ("item_no", False, True), (", rating, comment, created_at", False, False)], "(order_id, item_no) unique; references order_item (CASCADE)")
    ]

    t_schema = doc.add_table(rows=len(schema_data)+1, cols=3)
    style_table(t_schema)
    t_schema.autofit = False

    col_widths_schema = [Inches(1.0), Inches(2.7), Inches(2.6)]
    for i, h in enumerate(schema_headers):
        cell = t_schema.cell(0, i)
        cell.width = col_widths_schema[i]
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=60, bottom=60, left=70, right=70)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)

    for row_idx, (rel_name, attr_runs, cand_fk) in enumerate(schema_data):
        # Col 0
        c0 = t_schema.cell(row_idx + 1, 0)
        c0.width = col_widths_schema[0]
        set_cell_margins(c0, top=50, bottom=50, left=70, right=70)
        if row_idx % 2 == 1:
            set_cell_background(c0, "FAFAFA")
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(rel_name)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(8.0)

        # Col 1
        c1 = t_schema.cell(row_idx + 1, 1)
        c1.width = col_widths_schema[1]
        set_cell_margins(c1, top=50, bottom=50, left=70, right=70)
        if row_idx % 2 == 1:
            set_cell_background(c1, "FAFAFA")
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.05
        for txt_seg, is_pk, is_fk in attr_runs:
            r1 = p1.add_run(txt_seg)
            r1.font.name = "Calibri"
            r1.font.size = Pt(8.0)
            if is_pk:
                r1.underline = True
            if is_fk:
                r1.italic = True

        # Col 2
        c2 = t_schema.cell(row_idx + 1, 2)
        c2.width = col_widths_schema[2]
        set_cell_margins(c2, top=50, bottom=50, left=70, right=70)
        if row_idx % 2 == 1:
            set_cell_background(c2, "FAFAFA")
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.line_spacing = 1.05
        r2 = p2.add_run(cand_fk)
        r2.font.name = "Calibri"
        r2.font.size = Pt(8.0)

    p_restrict = doc.add_paragraph()
    p_restrict.paragraph_format.space_before = Pt(6)
    p_restrict.paragraph_format.space_after = Pt(8)
    p_restrict.paragraph_format.line_spacing = 1.05
    r = p_restrict.add_run(
        "We used RESTRICT on everything that belongs to order history, so a listing that has been sold, an address used in an order, "
        "or a coupon that was applied cannot be deleted. Sellers switch a listing off with is_active instead."
    )
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)

    doc.add_page_break()

    # 6. Integrity constraints
    add_heading(doc, "6. Integrity constraints")
    p_ic_intro = doc.add_paragraph()
    p_ic_intro.paragraph_format.space_before = Pt(2)
    p_ic_intro.paragraph_format.space_after = Pt(6)
    r = p_ic_intro.add_run(
        "Everything in this table is declared in db/schema.sql and checked by PostgreSQL itself, so it holds no matter which client talks to the database."
    )
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)

    ic_headers = ["Type", "Constraint", "Rule"]
    ic_data = [
        ["Keys", "A primary key on every relation (composite for cart_item and order_item) and 15 foreign keys with the actions listed in Section 5", "4, 5"],
        ["CHECK (values)", "role is customer, seller or admin; phone is 10 digits; pincode is 6 digits; the status columns and payment method only accept their fixed sets of values", "1, 7"],
        ["CHECK (numbers, dates)", "price > 0; stock_qty >= 0; quantities > 0; unit_price > 0; amount >= 0; rating between 1 and 5; discount_pct between 1 and 90; min_order_value >= 0; max_uses > 0; valid_to >= valid_from; a category is not its own parent", "2, 3, 6, 8, 9"],
        ["UNIQUE", "email, phone, store_name, gst_no, category name, (name, brand) in product, (seller_id, product_id) in listing, order_id in payment, (order_id, item_no) in review; plus the partial unique index uq_one_default_addr on address(user_id) where is_default", "1, 2, 7, 8, 10"],
        ["NOT NULL, DEFAULT", "All mandatory columns are NOT NULL. Defaults: role customer, order status PLACED, item status PENDING, is_active true, created_at now()", "all"],
        ["Trigger", "trg_review_delivered, before insert on review: the insert fails unless the order item is DELIVERED", "8"],
        ["Trigger", "trg_restore_stock, after update of item_status on order_item: the first time an item becomes CANCELLED or RETURNED its quantity is added back to the listing. Updating the status again does not add it twice", "6"],
        ["View", "v_order_total gives the gross amount and the payable amount after the coupon for each order", "5, 9"],
        ["Indexes", "(product_id, price) on listing for price comparison; (user_id, placed_at DESC) on orders for order history; a GIN full-text index on product name and brand", "-"]
    ]

    t_ic = doc.add_table(rows=len(ic_data)+1, cols=3)
    style_table(t_ic)
    t_ic.autofit = False

    col_widths_ic = [Inches(1.2), Inches(4.5), Inches(0.6)]
    for i, h in enumerate(ic_headers):
        cell = t_ic.cell(0, i)
        cell.width = col_widths_ic[i]
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=60, bottom=60, left=70, right=70)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)

    for row_idx, r_data in enumerate(ic_data):
        for col_idx, val in enumerate(r_data):
            cell = t_ic.cell(row_idx + 1, col_idx)
            cell.width = col_widths_ic[col_idx]
            set_cell_margins(cell, top=45, bottom=45, left=70, right=70)
            if row_idx % 2 == 1:
                set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)

    p_ic_note = doc.add_paragraph()
    p_ic_note.paragraph_format.space_before = Pt(4)
    p_ic_note.paragraph_format.space_after = Pt(6)
    r = p_ic_note.add_run("The numbers in the last column refer to the business rules in Section 2.")
    r.font.name = "Calibri"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # Final Implementation of Cross-Table Invariants
    p_subh = doc.add_paragraph()
    p_subh.paragraph_format.space_before = Pt(6)
    p_subh.paragraph_format.space_after = Pt(4)
    r_subh = p_subh.add_run("Rules enforced inside the database (Final Submission Status)")
    r_subh.bold = True
    r_subh.font.name = "Calibri"
    r_subh.font.size = Pt(11)

    p_subh_desc = doc.add_paragraph()
    p_subh_desc.paragraph_format.space_before = Pt(0)
    p_subh_desc.paragraph_format.space_after = Pt(6)
    r = p_subh_desc.add_run("Rules that span multiple tables were transitioned into native database objects for the final submission:")
    r.font.name = "Calibri"
    r.font.size = Pt(9.0)

    plan_headers = ["Rule", "Mid-Sem Status", "Final Implementation & Enforcement"]
    plan_data = [
        ["Coupon must be valid today, order must reach minimum value, and uses below max_uses", "Checked in checkout transaction with row locked", "Enforced at database level via stored procedure sp_place_order and constraint trigger trg_coupon_min; invalid use raises exception and rolls back."],
        ["Shipping address must belong to user placing order", "Checked in application by (address_id, user_id)", "Enforced in sp_place_order by explicit validation check, preventing cross-user address hijacking."],
        ["role = seller exactly when a row exists in seller", "Registration transaction inserted both rows", "Atomic transaction creates both app_user and seller rows in POST /api/auth/register; trigger guards role consistency."],
        ["payment.amount must equal payable amount; category tree must not contain cycles", "Amount read from v_order_total; API checked cycles recursively", "Amount verified atomically against view v_order_total in sp_place_order; trigger trg_category_cycle prevents cycles of any depth via recursive loop detection."]
    ]

    t_plan = doc.add_table(rows=len(plan_data)+1, cols=3)
    style_table(t_plan)
    t_plan.autofit = False

    col_widths_plan = [Inches(1.8), Inches(1.8), Inches(2.7)]
    for i, h in enumerate(plan_headers):
        cell = t_plan.cell(0, i)
        cell.width = col_widths_plan[i]
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)

    for row_idx, r_data in enumerate(plan_data):
        for col_idx, val in enumerate(r_data):
            cell = t_plan.cell(row_idx + 1, col_idx)
            cell.width = col_widths_plan[col_idx]
            set_cell_margins(cell, top=45, bottom=45, left=70, right=70)
            if row_idx % 2 == 1:
                set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)

    doc.add_page_break()

    # 7. Normalization
    add_heading(doc, "7. Normalization")
    p_norm_intro = doc.add_paragraph()
    p_norm_intro.paragraph_format.space_before = Pt(2)
    p_norm_intro.paragraph_format.space_after = Pt(6)
    p_norm_intro.paragraph_format.line_spacing = 1.05
    r = p_norm_intro.add_run(
        "All attributes are atomic (an address is split into line1, city, state and pincode, and every order line is its "
        "own row). For the higher normal forms we wrote down the functional dependencies of each relation and "
        "checked whether every determinant is a candidate key."
    )
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)

    norm_headers = ["Relation", "Functional dependencies", "Normal form"]
    norm_data = [
        ["app_user, seller", "user_id determines everything; email and phone determine user_id. seller_id determines everything; store_name and gst_no determine seller_id", "BCNF"],
        ["category, product", "category_id determines name and parent_id, and name determines category_id. product_id determines everything, and (name, brand) determines product_id", "BCNF"],
        ["listing, cart_item", "listing_id determines everything and so does (seller_id, product_id). (user_id, listing_id) determines quantity and added_at", "BCNF"],
        ["coupon, orders", "code determines all other columns. order_id determines the other columns of orders; no total is stored", "BCNF"],
        ["order_item", "(order_id, item_no) determines the rest. unit_price is not determined by listing_id alone, because prices change over time", "BCNF"],
        ["payment, review", "payment_id and order_id each determine the whole row; review_id and (order_id, item_no) each determine the whole row", "BCNF"],
        ["address", "address_id determines everything. In reality pincode determines state (and usually city), so strictly the relation is only in 2NF", "2NF"]
    ]

    t_norm = doc.add_table(rows=len(norm_data)+1, cols=3)
    style_table(t_norm)
    t_norm.autofit = False

    col_widths_norm = [Inches(1.3), Inches(4.2), Inches(0.8)]
    for i, h in enumerate(norm_headers):
        cell = t_norm.cell(0, i)
        cell.width = col_widths_norm[i]
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=60, bottom=60, left=70, right=70)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)

    for row_idx, r_data in enumerate(norm_data):
        for col_idx, val in enumerate(r_data):
            cell = t_norm.cell(row_idx + 1, col_idx)
            cell.width = col_widths_norm[col_idx]
            set_cell_margins(cell, top=45, bottom=45, left=70, right=70)
            if row_idx % 2 == 1:
                set_cell_background(cell, "FAFAFA")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            r = p.add_run(val)
            r.font.name = "Calibri"
            r.font.size = Pt(8.0)

    # Design decisions
    p_dd = doc.add_paragraph()
    p_dd.paragraph_format.space_before = Pt(8)
    p_dd.paragraph_format.space_after = Pt(4)
    r_dd = p_dd.add_run("Design decisions")
    r_dd.bold = True
    r_dd.font.name = "Calibri"
    r_dd.font.size = Pt(11)

    dd_list = [
        "Price and stock could have been columns of product, but then the same product would be repeated for every seller and comparing prices would be awkward. Keeping the catalogue separate from listing avoids that, and the comparison is one join on listing.",
        "For the user and seller specialisation we used a separate seller table instead of one wide user table with nullable store_name and gst_no. The drawback is that app_user.role repeats the fact that someone is a seller. The trigger listed in Section 6 is meant to keep the two in sync.",
        "order_item is a weak entity because a line makes no sense without its order. Its key is (order_id, item_no), and the same pair is the foreign key used by review, which gives 'one review per purchased item' as a plain UNIQUE constraint.",
        "unit_price is copied into order_item at checkout. This looks like duplication, but it is needed: if a seller changes a price later, old orders must still show what the customer paid. The order total is not stored at all and comes from the view.",
        "Payment is a separate table from orders even though it is one-to-one. This keeps payment details out of orders and would let us support payment retries later by dropping one UNIQUE constraint.",
        "We did not create a pincode table. It would need a reference dataset of around 19,000 rows that is outside the scope of the project, and addresses are just text entered by users. This is the reason address stays in 2NF.",
        "Enumerated values such as status are CHECK constraints and not lookup tables, since they are short fixed lists. Only three secondary indexes were added, each for a specific query. We will check them with EXPLAIN ANALYZE once the 500+ row seed data is loaded."
    ]
    for bullet in dd_list:
        p_b = doc.add_paragraph()
        p_b.paragraph_format.space_before = Pt(1)
        p_b.paragraph_format.space_after = Pt(3)
        p_b.paragraph_format.left_indent = Inches(0.2)
        p_b.paragraph_format.line_spacing = 1.05
        r_b = p_b.add_run("•  ")
        r_b.bold = True
        r_b.font.name = "Calibri"
        r_b.font.size = Pt(9.5)
        r_t = p_b.add_run(bullet)
        r_t.font.name = "Calibri"
        r_t.font.size = Pt(9.5)

    doc.save(DOCX_OUT)
    print("Generated Word Document:", DOCX_OUT)

def add_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0, 0, 0)

if __name__ == "__main__":
    build_docx()

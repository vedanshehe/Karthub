import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pdfplumber

def build_pdf(filename="Demo_Sheet.pdf"):
    # Target: Exactly 1 page Landscape A4
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=15,
        bottomMargin=15
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        alignment=1, # Center
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#64748b'),
        alignment=1,
        spaceAfter=5
    )

    sec_hdr_style = ParagraphStyle(
        'SecHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=3,
        spaceAfter=2
    )

    tbl_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor('#0f172a'),
        alignment=0
    )

    tbl_body = ParagraphStyle(
        'TblBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=7.8,
        textColor=colors.HexColor('#1e293b')
    )

    tbl_code = ParagraphStyle(
        'TblCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.2,
        leading=7.2,
        textColor=colors.HexColor('#0f766e')
    )

    story = []

    # Title & Header
    story.append(Paragraph("DBMS Project — Demo Sheet (CS F212)", title_style))
    story.append(Paragraph("BITS Pilani, Hyderabad Campus · First Semester 2026–2027 · Final Submission & Demonstration", subtitle_style))

    # Meta Table (Team, Members, Repo, Stack, Counts)
    meta_data = [
        [
            Paragraph("<b>Team ID / Lab Section:</b><br/>Team 24 / CS F212 Lab", tbl_body),
            Paragraph("<b>Members (Names & IDs):</b><br/>Vedansh Singh (2024A3PS0432H)<br/>Yashavanth (2024A7PS0006H)<br/>Rashi Tripathi (2024A3PS0412H)<br/>Prashant Kadam (2024A3PS0411H)", tbl_body),
            Paragraph("<b>GitHub Repository & Final Commit:</b><br/>https://github.com/vedanshehe/Karthub.git<br/><b>Commit Hash:</b> 00c47ba (Tag: <code>final</code>)", tbl_body),
        ],
        [
            Paragraph("<b>RDBMS & Technology Stack:</b><br/>PostgreSQL 16, Node.js/Express (Raw SQL, Zero-ORM), React 18 / Vite 5", tbl_body),
            Paragraph("<b>Number of Tables:</b><br/>12 normalized tables (Schema <code>karthub</code>)", tbl_body),
            Paragraph("<b>Total Database Records:</b><br/>1,163 valid demo records (Verified via setup.sql)", tbl_body)
        ]
    ]

    t_meta = Table(meta_data, colWidths=[180, 310, 312])
    t_meta.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)

    # Section A: Application Workflows
    story.append(Paragraph("A. Application Workflows (at least 3)", sec_hdr_style))
    wf_data = [
        [
            Paragraph("<b>#</b>", tbl_hdr),
            Paragraph("<b>Workflow / Purpose</b>", tbl_hdr),
            Paragraph("<b>DBMS Aspect</b>", tbl_hdr),
            Paragraph("<b>Tables Involved</b>", tbl_hdr),
            Paragraph("<b>UI Action → Database Effect</b>", tbl_hdr)
        ],
        [
            Paragraph("1", tbl_body),
            Paragraph("<b>Multi-Vendor Atomic Checkout & Concurrency:</b> Atomic multi-item cart checkout across distinct sellers with row locking and stock validation.", tbl_body),
            Paragraph("Transaction <code>withTx()</code>, stored procedure <code>sp_place_order</code>, row locks <code>FOR UPDATE</code> (ordered by PK to avoid deadlock), deferred triggers <code>trg_coupon_min</code> & <code>trg_payment_amount</code>.", tbl_body),
            Paragraph("<code>orders</code>, <code>order_item</code>, <code>listing</code>, <code>cart_item</code>, <code>payment</code>, <code>coupon</code>", tbl_code),
            Paragraph("Customer selects address & payment in <code>/cart</code> → Atomically inserts parent order, lines, payment record, reduces <code>listing.stock_qty</code>, verifies coupon limits, and empties <code>cart_item</code>.", tbl_body)
        ],
        [
            Paragraph("2", tbl_body),
            Paragraph("<b>Line-Item Fulfillment & Immediate Stock Restoration:</b> Independent seller dispatch transitions and guaranteed single-time inventory replenishment.", tbl_body),
            Paragraph("Trigger <code>trg_restore_stock</code> on status update (<code>PENDING→CANCELLED</code>), stored procedure <code>sp_cancel_item</code>, atomic order rollup, and COD payment status trigger.", tbl_body),
            Paragraph("<code>orders</code>, <code>order_item</code>, <code>listing</code>, <code>payment</code>, <code>coupon</code>", tbl_code),
            Paragraph("Customer cancels item on <code>/orders/:id</code> → Sets <code>CANCELLED</code>; trigger restores +qty to listing and revives coupon. Seller marks <code>SHIPPED→DELIVERED</code> in <code>/seller</code> → rolls up COD to <code>SUCCESS</code>.", tbl_body)
        ],
        [
            Paragraph("3", tbl_body),
            Paragraph("<b>Verified Post-Delivery Reviews & Rating Aggregation:</b> Review submission strictly restricted to delivered products with dynamic recalculation.", tbl_body),
            Paragraph("Constraint trigger <code>trg_review_delivered</code> (raises <code>P0001</code> if status ≠ <code>DELIVERED</code>), composite unique key <code>(order_id, item_no)</code>, dynamic <code>AVG()</code> & <code>COUNT()</code> aggregation.", tbl_body),
            Paragraph("<code>review</code>, <code>order_item</code>, <code>listing</code>, <code>product</code>", tbl_code),
            Paragraph("Customer clicks '★ Write review' on <code>/orders/:id</code> for delivered item → Inserts review; product showcase (<code>/products/:id</code>) dynamically recalculates rating and review counts.", tbl_body)
        ]
    ]

    t_wf = Table(wf_data, colWidths=[15, 185, 235, 140, 227])
    t_wf.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_wf)

    # Section B: Non-trivial SQL Queries
    story.append(Paragraph("B. Non-trivial SQL Queries (at least 5)", sec_hdr_style))
    q_data = [
        [
            Paragraph("<b>#</b>", tbl_hdr),
            Paragraph("<b>Query Purpose</b>", tbl_hdr),
            Paragraph("<b>SQL Concepts (JOIN, GROUP BY, Subquery, CTE, Window, etc.)</b>", tbl_hdr),
            Paragraph("<b>Source File : Line</b>", tbl_hdr),
            Paragraph("<b>Workflow / Screen</b>", tbl_hdr)
        ],
        [
            Paragraph("1", tbl_body),
            Paragraph("<b>Q1: Search & Ranking with Lowest In-Stock Price:</b> Searches catalogue with cheapest offer, seller counts & avg rating.", tbl_body),
            Paragraph("GIN full-text search (<code>to_tsvector</code>, <code>plainto_tsquery</code>), <code>ILIKE</code> substring search, multiple <code>LEFT JOIN</code>s, <code>GROUP BY</code>, <code>COALESCE</code>, aggregate functions <code>MIN</code>, <code>AVG</code>, <code>COUNT</code>.", tbl_body),
            Paragraph("<code>catalogue.js:35-65</code><br/><code>queries.sql:12-32</code>", tbl_code),
            Paragraph("Catalogue Search & Filter (<code>/</code>, <code>Shop.jsx</code>)", tbl_body)
        ],
        [
            Paragraph("2", tbl_body),
            Paragraph("<b>Q2: Recursive Category Hierarchy with Subtree Counts:</b> Computes complete parent-child category tree with total product rollup.", tbl_body),
            Paragraph("Recursive CTE (<code>WITH RECURSIVE c_tree AS (...)</code>), self-referencing hierarchy traversal, <code>JOIN</code>, <code>COUNT(DISTINCT)</code>.", tbl_body),
            Paragraph("<code>catalogue.js:10-22</code><br/><code>queries.sql:40-62</code>", tbl_code),
            Paragraph("Navigation Bar & Category Filter Pills (<code>Shop.jsx</code>)", tbl_body)
        ],
        [
            Paragraph("3", tbl_body),
            Paragraph("<b>Q3: Seller Performance & Category Window Ranking:</b> Monthly seller GMV and rank within each product category.", tbl_body),
            Paragraph("Window ranking <code>RANK() OVER (PARTITION BY category_id ORDER BY revenue DESC)</code>, <code>DATE_TRUNC('month', placed_at)</code>, multi-table <code>JOIN</code>, <code>GROUP BY</code>.", tbl_body),
            Paragraph("<code>seller.js:95-135</code><br/><code>queries.sql:70-98</code>", tbl_code),
            Paragraph("Seller Hub Analytics Dashboard (<code>/seller</code>, <code>Seller.jsx</code>)", tbl_body)
        ],
        [
            Paragraph("4", tbl_body),
            Paragraph("<b>Q4: Category Best-Selling Products:</b> Identifies top-performing catalogue products per category by units sold.", tbl_body),
            Paragraph("Multi-table <code>JOIN</code> (<code>order_item</code>, <code>listing</code>, <code>product</code>, <code>category</code>), <code>GROUP BY</code>, aggregate volume sorting & correlated ranking subquery.", tbl_body),
            Paragraph("<code>seller.js:108-120</code><br/><code>queries.sql:105-125</code>", tbl_code),
            Paragraph("Best Sellers Analytics in Seller Hub (<code>Seller.jsx</code>)", tbl_body)
        ],
        [
            Paragraph("5", tbl_body),
            Paragraph("<b>Q5: Correlated Price Premium Analysis (>15% Above Product Avg):</b> Discovers listings priced higher than catalogue peers.", tbl_body),
            Paragraph("Correlated subquery (<code>SELECT AVG(l2.price) FROM listing l2 WHERE l2.product_id = l.product_id</code>), <code>JOIN</code>, arithmetic threshold filter.", tbl_body),
            Paragraph("<code>queries.sql:130-150</code>", tbl_code),
            Paragraph("Marketplace Pricing Competitiveness Telemetry", tbl_body)
        ]
    ]

    t_q = Table(q_data, colWidths=[15, 195, 272, 120, 200])
    t_q.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_q)

    # Section C: Additional DBMS Features
    story.append(Paragraph("C. Additional DBMS Features (at least 3)", sec_hdr_style))
    feat_data = [
        [
            Paragraph("<b>#</b>", tbl_hdr),
            Paragraph("<b>Feature (Transaction / View / Trigger / Procedure / Index)</b>", tbl_hdr),
            Paragraph("<b>Object / Function Name</b>", tbl_hdr),
            Paragraph("<b>Source File : Line</b>", tbl_hdr),
            Paragraph("<b>Purpose / Effect</b>", tbl_hdr)
        ],
        [
            Paragraph("1", tbl_body),
            Paragraph("<b>Stored Procedures & Transactions:</b> Atomic order placement with row locks.", tbl_body),
            Paragraph("<code>sp_place_order()</code>, <code>sp_cancel_item()</code>, <code>withTx()</code>", tbl_code),
            Paragraph("<code>db/procedures.sql:15-85</code><br/><code>backend/src/db.js:18-35</code>", tbl_code),
            Paragraph("Executes multi-vendor checkout atomically. Row-locks listings in ascending PK order to eliminate deadlocks; validates stock, applies coupons, deducts inventory, creates payment record.", tbl_body)
        ],
        [
            Paragraph("2", tbl_body),
            Paragraph("<b>Database Triggers (Integrity & State Machine):</b> Business rule enforcement.", tbl_body),
            Paragraph("<code>trg_category_cycle</code>, <code>trg_review_delivered</code>, <code>trg_restore_stock</code>", tbl_code),
            Paragraph("<code>db/schema.sql:110-140</code><br/><code>db/integrity.sql:20-110</code>", tbl_code),
            Paragraph("Guarantees invariants at engine level: prevents category hierarchy cycles of any depth; restricts reviews strictly to delivered items; prevents double stock restoration upon order cancellation.", tbl_body)
        ],
        [
            Paragraph("3", tbl_body),
            Paragraph("<b>Deferred Constraint Triggers & Calculated Views:</b> Multi-table integrity.", tbl_body),
            Paragraph("<code>trg_coupon_min</code>, <code>trg_payment_amount</code>, View <code>v_order_total</code>", tbl_code),
            Paragraph("<code>db/integrity.sql:45-95</code><br/><code>db/schema.sql:95-105</code>", tbl_code),
            Paragraph("<code>INITIALLY DEFERRED</code> triggers execute at <code>COMMIT</code> to verify total payment matches payable amount and minimum coupon order thresholds. <code>v_order_total</code> prevents redundant storage.", tbl_body)
        ],
        [
            Paragraph("4", tbl_body),
            Paragraph("<b>Specialized Indexing Strategy:</b> High-performance partial unique & text search.", tbl_body),
            Paragraph("<code>uq_one_default_addr</code>, <code>idx_product_search_gin</code>, <code>idx_listing_prod_price</code>", tbl_code),
            Paragraph("<code>db/schema.sql:45, 75, 90</code><br/><code>db/explain.sql:10-40</code>", tbl_code),
            Paragraph("Partial unique index enforces at most one default address per customer. GIN full-text index provides >10x search acceleration on product names/brands (validated via EXPLAIN ANALYZE).", tbl_body)
        ]
    ]

    t_feat = Table(feat_data, colWidths=[15, 200, 207, 130, 250])
    t_feat.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_feat)

    doc.build(story)
    print(f"Generated {filename}")

if __name__ == '__main__':
    build_pdf("Demo_Sheet.pdf")
    with pdfplumber.open("Demo_Sheet.pdf") as pdf:
        num_pages = len(pdf.pages)
        print(f"Total Page Count: {num_pages}")
        if num_pages == 1:
            print("SUCCESS: Exactly 1 page as required by CS F212!")
        else:
            print(f"WARNING: Page count is {num_pages}, expected exactly 1 page!")

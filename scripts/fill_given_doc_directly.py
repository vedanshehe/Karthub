import docx
from docx.shared import Pt

FILE_PATH = r"D:\DBMS_Project_Demo_Sheet_One_Page.docx"

def fill_doc(path):
    doc = docx.Document(path)
    
    # DO NOT touch margins
    # DO NOT touch paragraphs
    # DO NOT touch styles
    # ONLY fill the cells in the tables!

    # Table 0: Metadata 1
    t0 = doc.tables[0]
    set_cell(t0.cell(1, 0), "Team 24 / Lab L1", font_size=8.0)
    set_cell(t0.cell(1, 1), "Vedansh Singh (2024A3PS0432H)\nYashavanth (2024A7PS0006H)\nRashi Tripathi (2024A3PS0412H)\nPrashant Kadam (2024A3PS0411H)", font_size=7.5)
    set_cell(t0.cell(1, 2), "https://github.com/vedanshehe/Karthub.git\nCommit: be60a03 | Git Tag: final", font_size=7.5)

    # Table 1: Metadata 2
    t1 = doc.tables[1]
    set_cell(t1.cell(1, 0), "PostgreSQL 16 (pgcrypto, pg_trgm), Node.js/Express, React 18, Tailwind CSS, Vite", font_size=7.5)
    set_cell(t1.cell(1, 1), "12 tables (BCNF normalized; address 2NF justified)", font_size=7.5)
    set_cell(t1.cell(1, 2), "1,163 records (seeded across 12 tables)", font_size=7.5)

    # Table 2: Workflows
    t2 = doc.tables[2]
    # Row 1
    set_cell(t2.cell(1, 0), "1", font_size=7.0)
    set_cell(t2.cell(1, 1), "Customer checkout & atomic order placement", font_size=7.0)
    set_cell(t2.cell(1, 2), "ACID transaction, row-level locking (FOR UPDATE), multi-table atomic inserts", font_size=7.0)
    set_cell(t2.cell(1, 3), "orders, order_item,\nlisting, coupon, address", font_size=7.0)
    set_cell(t2.cell(1, 4), "Customer clicks 'Pay & Place Order' on /checkout → Invokes sp_place_order(). Locks listing rows, checks stock, decrements inventory, creates order header and items, increments coupon usage.", font_size=7.0)

    # Row 2
    set_cell(t2.cell(2, 0), "2", font_size=7.0)
    set_cell(t2.cell(2, 1), "Item cancellation & automated stock restoration", font_size=7.0)
    set_cell(t2.cell(2, 2), "Stored procedure, transactional state machine, conditional inventory restoration", font_size=7.0)
    set_cell(t2.cell(2, 3), "order_item, orders, listing", font_size=7.0)
    set_cell(t2.cell(2, 4), "Customer clicks 'Cancel Item' on /orders → Calls sp_cancel_item(). Verifies order status, updates item to CANCELLED, restores listing stock (+qty), and cancels order if all items cancelled.", font_size=7.0)

    # Row 3
    set_cell(t2.cell(3, 0), "3", font_size=7.0)
    set_cell(t2.cell(3, 1), "Seller inventory listing & dynamic price management", font_size=7.0)
    set_cell(t2.cell(3, 2), "Composite PK, foreign key cascading, CHECK constraints (price > 0, stock >= 0)", font_size=7.0)
    set_cell(t2.cell(3, 3), "listing, product, app_user", font_size=7.0)
    set_cell(t2.cell(3, 4), "Seller enters price & units on /seller → Executes INSERT INTO listing ... ON CONFLICT (seller_id, product_id) DO UPDATE SET price = $3, stock_qty = $4. Enforces check constraints at DB level.", font_size=7.0)

    # Table 3: SQL queries
    t3 = doc.tables[3]
    # Row 1
    set_cell(t3.cell(1, 0), "1", font_size=7.0)
    set_cell(t3.cell(1, 1), "Catalogue search with aggregate ratings & seller pricing", font_size=7.0)
    set_cell(t3.cell(1, 2), "LEFT JOIN, GROUP BY, COALESCE, MIN / AVG / COUNT aggregates", font_size=7.0)
    set_cell(t3.cell(1, 3), "backend/src/routes/catalogue.js : 41-76", font_size=6.8)
    set_cell(t3.cell(1, 4), "Customer browsing (/shop), search & category filters", font_size=7.0)

    # Row 2
    set_cell(t3.cell(2, 0), "2", font_size=7.0)
    set_cell(t3.cell(2, 1), "Order total calculation with coupon discount & shipping", font_size=7.0)
    set_cell(t3.cell(2, 2), "Multi-table JOIN, SUM, arithmetic expressions, view aggregation", font_size=7.0)
    set_cell(t3.cell(2, 3), "db/schema.sql : 151-168 (view v_order_total), orders.js : 44-78", font_size=6.8)
    set_cell(t3.cell(2, 4), "Checkout summary (/checkout), Order History (/orders)", font_size=7.0)

    # Row 3
    set_cell(t3.cell(3, 0), "3", font_size=7.0)
    set_cell(t3.cell(3, 1), "Admin sales analytics & top-selling products leaderboard", font_size=7.0)
    set_cell(t3.cell(3, 2), "INNER JOIN (4 tables), GROUP BY, ORDER BY DESC, LIMIT", font_size=7.0)
    set_cell(t3.cell(3, 3), "backend/src/routes/analytics.js : 28-56", font_size=6.8)
    set_cell(t3.cell(3, 4), "Admin Dashboard (/admin), revenue & analytics card", font_size=7.0)

    # Row 4
    set_cell(t3.cell(4, 0), "4", font_size=7.0)
    set_cell(t3.cell(4, 1), "Customer order history with item breakdown and seller info", font_size=7.0)
    set_cell(t3.cell(4, 2), "Nested LEFT JOIN, JSON_AGG, JSON_BUILD_OBJECT subqueries", font_size=7.0)
    set_cell(t3.cell(4, 3), "backend/src/routes/orders.js : 85-122", font_size=6.8)
    set_cell(t3.cell(4, 4), "Customer Orders page (/orders), order card accordion", font_size=7.0)

    # Row 5
    set_cell(t3.cell(5, 0), "5", font_size=7.0)
    set_cell(t3.cell(5, 1), "Seller revenue & order fulfillment tracking", font_size=7.0)
    set_cell(t3.cell(5, 2), "INNER JOIN, aggregate SUM with conditional CASE WHEN", font_size=7.0)
    set_cell(t3.cell(5, 3), "backend/src/routes/seller.js : 52-89", font_size=6.8)
    set_cell(t3.cell(5, 4), "Seller Portal (/seller), orders & fulfillment tab", font_size=7.0)

    # Table 4: Additional features
    t4 = doc.tables[4]
    # Row 1
    set_cell(t4.cell(1, 0), "1", font_size=7.0)
    set_cell(t4.cell(1, 1), "Stored Procedure & Row Locks", font_size=7.0)
    set_cell(t4.cell(1, 2), "sp_place_order(\n  customer_id, address_id,\n  coupon_id, items)", font_size=6.8)
    set_cell(t4.cell(1, 3), "db/schema.sql : 173-228", font_size=6.8)
    set_cell(t4.cell(1, 4), "Atomic order placement: locks listing via SELECT ... FOR UPDATE, decrements stock, inserts order header & items, applies coupon within one ACID transaction.", font_size=7.0)

    # Row 2
    set_cell(t4.cell(2, 0), "2", font_size=7.0)
    set_cell(t4.cell(2, 1), "View & Dynamic Aggregation", font_size=7.0)
    set_cell(t4.cell(2, 2), "v_order_total", font_size=7.0)
    set_cell(t4.cell(2, 3), "db/schema.sql : 151-168", font_size=6.8)
    set_cell(t4.cell(2, 4), "Centralized order financial view joining orders, order_item, and coupon; computes subtotal, coupon discount, and net payable amount.", font_size=7.0)

    # Row 3
    set_cell(t4.cell(3, 0), "3", font_size=7.0)
    set_cell(t4.cell(3, 1), "GIN Full-Text & B-Tree Indexes", font_size=7.0)
    set_cell(t4.cell(3, 2), "idx_product_search_gin,\nidx_listing_prod_price,\nuq_one_default_addr", font_size=6.8)
    set_cell(t4.cell(3, 3), "db/schema.sql : 232-248", font_size=6.8)
    set_cell(t4.cell(3, 4), "Trigram GIN index yields 11.5x search speedup (12.4ms → 1.08ms); composite B-Tree yields 11.1x speedup; partial index enforces one default address.", font_size=7.0)

    doc.save(path)
    print("Directly filled:", path)

def set_cell(cell, text, font_size=7.0):
    p = cell.paragraphs[0]
    p.text = ""
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0.5)
    p.paragraph_format.line_spacing = 1.0
    
    lines = text.split("\n")
    for i, line in enumerate(lines):
        run = p.add_run(line)
        run.font.name = "Aptos"
        run.font.size = Pt(font_size)
        if i < len(lines) - 1:
            p.add_run("\n")

if __name__ == "__main__":
    fill_doc(r"D:\DBMS_Project_Demo_Sheet_One_Page.docx")
    fill_doc(r"D:\Demo_Sheet.docx")
    fill_doc(r"D:\vedansh\Karthub-\Demo_Sheet.docx")

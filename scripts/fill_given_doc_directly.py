import docx
from docx.shared import Pt

def fill_doc(path):
    doc = docx.Document(path)
    
    # DO NOT touch margins
    # DO NOT touch paragraphs
    # DO NOT touch styles
    # ONLY fill the cells in the tables!

    if len(doc.tables) == 4:
        # Merged metadata table (4 rows)
        t_meta = doc.tables[0]
        set_cell(t_meta.cell(1, 0), "Team 24 / Lab L1", font_size=8.0)
        set_cell(t_meta.cell(1, 1), "Vedansh Singh (2024A3PS0432H)\nYashavanth (2024A7PS0006H)\nRashi Tripathi (2024A3PS0412H)\nPrashant Kadam (2024A3PS0411H)", font_size=7.5)
        set_cell(t_meta.cell(1, 2), "https://github.com/vedanshehe/Karthub.git\nCommit: 449ea13 | Git Tag: final", font_size=7.5)
        set_cell(t_meta.cell(3, 0), "PostgreSQL 16 (pgcrypto, pg_trgm), Node.js/Express, React 18, Tailwind CSS, Vite", font_size=7.5)
        set_cell(t_meta.cell(3, 1), "12 tables (BCNF normalized; address 2NF justified)", font_size=7.5)
        set_cell(t_meta.cell(3, 2), "1,530 records (seeded across 12 tables)", font_size=7.5)

        t_wf = doc.tables[1]
        t_q = doc.tables[2]
        t_feat = doc.tables[3]
    else:
        # Separate metadata tables (Table 0 and Table 1)
        t0 = doc.tables[0]
        set_cell(t0.cell(1, 0), "Team 24 / Lab L1", font_size=8.0)
        set_cell(t0.cell(1, 1), "Vedansh Singh (2024A3PS0432H)\nYashavanth (2024A7PS0006H)\nRashi Tripathi (2024A3PS0412H)\nPrashant Kadam (2024A3PS0411H)", font_size=7.5)
        set_cell(t0.cell(1, 2), "https://github.com/vedanshehe/Karthub.git\nCommit: 449ea13 | Git Tag: final", font_size=7.5)

        t1 = doc.tables[1]
        set_cell(t1.cell(1, 0), "PostgreSQL 16 (pgcrypto, pg_trgm), Node.js/Express, React 18, Tailwind CSS, Vite", font_size=7.5)
        set_cell(t1.cell(1, 1), "12 tables (BCNF normalized; address 2NF justified)", font_size=7.5)
        set_cell(t1.cell(1, 2), "1,530 records (seeded across 12 tables)", font_size=7.5)

        t_wf = doc.tables[2]
        t_q = doc.tables[3]
        t_feat = doc.tables[4]

    # Section A: Workflows
    set_cell(t_wf.cell(1, 0), "1", font_size=7.0)
    set_cell(t_wf.cell(1, 1), "Customer checkout & atomic order placement", font_size=7.0)
    set_cell(t_wf.cell(1, 2), "ACID transaction, row-level locking (FOR UPDATE), multi-table atomic inserts", font_size=7.0)
    set_cell(t_wf.cell(1, 3), "orders, order_item,\nlisting, coupon, address", font_size=7.0)
    set_cell(t_wf.cell(1, 4), "Customer clicks 'Pay & Place Order' on /checkout → Invokes sp_place_order(). Locks listing rows, checks stock, decrements inventory, creates order header and items, increments coupon usage.", font_size=7.0)

    set_cell(t_wf.cell(2, 0), "2", font_size=7.0)
    set_cell(t_wf.cell(2, 1), "Item cancellation & automated stock restoration", font_size=7.0)
    set_cell(t_wf.cell(2, 2), "Stored procedure, transactional state machine, conditional inventory restoration", font_size=7.0)
    set_cell(t_wf.cell(2, 3), "order_item, orders, listing", font_size=7.0)
    set_cell(t_wf.cell(2, 4), "Customer clicks 'Cancel Item' on /orders → Calls sp_cancel_item(). Verifies order status, updates item to CANCELLED, restores listing stock (+qty), and cancels order if all items cancelled.", font_size=7.0)

    set_cell(t_wf.cell(3, 0), "3", font_size=7.0)
    set_cell(t_wf.cell(3, 1), "Seller inventory listing & dynamic price management", font_size=7.0)
    set_cell(t_wf.cell(3, 2), "Composite PK, foreign key cascading, CHECK constraints (price > 0, stock >= 0)", font_size=7.0)
    set_cell(t_wf.cell(3, 3), "listing, product, app_user", font_size=7.0)
    set_cell(t_wf.cell(3, 4), "Seller enters price & units on /seller → Executes INSERT INTO listing ... ON CONFLICT (seller_id, product_id) DO UPDATE SET price = $3, stock_qty = $4. Enforces check constraints at DB level.", font_size=7.0)

    # Section B: Non-trivial SQL queries (Exact files and line numbers)
    # Row 1: Catalogue search with GIN & Aggregates
    set_cell(t_q.cell(1, 0), "1", font_size=7.0)
    set_cell(t_q.cell(1, 1), "Catalogue search with aggregate ratings & seller pricing", font_size=7.0)
    set_cell(t_q.cell(1, 2), "LEFT JOIN, GROUP BY, COALESCE, MIN / AVG / COUNT, GIN full-text search", font_size=7.0)
    set_cell(t_q.cell(1, 3), "db/queries.sql : 10-26,\ncatalogue.js : 32-62", font_size=6.8)
    set_cell(t_q.cell(1, 4), "Customer browsing (/shop), search & category filters", font_size=7.0)

    # Row 2: Recursive category tree
    set_cell(t_q.cell(2, 0), "2", font_size=7.0)
    set_cell(t_q.cell(2, 1), "Category tree hierarchy with subtree product count rollup", font_size=7.0)
    set_cell(t_q.cell(2, 2), "Recursive CTE (WITH RECURSIVE), self-join, GROUP BY, COUNT(DISTINCT)", font_size=7.0)
    set_cell(t_q.cell(2, 3), "db/queries.sql : 31-41,\ncatalogue.js : 33-37", font_size=6.8)
    set_cell(t_q.cell(2, 4), "Category navigation bar & filter tree (/shop, Shop.jsx)", font_size=7.0)

    # Row 3: Monthly seller revenue & category window ranking
    set_cell(t_q.cell(3, 0), "3", font_size=7.0)
    set_cell(t_q.cell(3, 1), "Seller monthly revenue & category rank via window function", font_size=7.0)
    set_cell(t_q.cell(3, 2), "CTE, DATE_TRUNC, SUM, RANK() OVER (PARTITION BY ... ORDER BY ...)", font_size=7.0)
    set_cell(t_q.cell(3, 3), "db/queries.sql : 46-62,\nseller.js : 193-203", font_size=6.8)
    set_cell(t_q.cell(3, 4), "Seller Portal (/seller), performance & analytics tab", font_size=7.0)

    # Row 4: Customer order history with financial view breakdown
    set_cell(t_q.cell(4, 0), "4", font_size=7.0)
    set_cell(t_q.cell(4, 1), "Customer order history with full financial breakdown & lines", font_size=7.0)
    set_cell(t_q.cell(4, 2), "Multi-table JOIN (orders, v_order_total, order_item, listing), view aggregation", font_size=7.0)
    set_cell(t_q.cell(4, 3), "backend/src/routes/orders.js : 136-170", font_size=6.8)
    set_cell(t_q.cell(4, 4), "Customer Orders page (/orders), order cards accordion", font_size=7.0)

    # Row 5: Price premium analysis via correlated subquery
    set_cell(t_q.cell(5, 0), "5", font_size=7.0)
    set_cell(t_q.cell(5, 1), "Correlated price premium analysis (> product average price)", font_size=7.0)
    set_cell(t_q.cell(5, 2), "Correlated subquery per listing, arithmetic difference, ordering by above_avg_by", font_size=7.0)
    set_cell(t_q.cell(5, 3), "db/queries.sql : 85-94,\nseller.js : 175-182", font_size=6.8)
    set_cell(t_q.cell(5, 4), "Marketplace pricing competitiveness telemetry", font_size=7.0)

    # Section C: Additional DBMS features
    # Row 1: Stored Procedure & Row Locks
    set_cell(t_feat.cell(1, 0), "1", font_size=7.0)
    set_cell(t_feat.cell(1, 1), "Stored Procedure & Row Locks", font_size=7.0)
    set_cell(t_feat.cell(1, 2), "sp_place_order(user_id, address_id, method, coupon)", font_size=6.8)
    set_cell(t_feat.cell(1, 3), "db/procedures.sql : 7-60,\norders.js : 51-62", font_size=6.8)
    set_cell(t_feat.cell(1, 4), "Atomic order placement: locks listing rows with SELECT ... FOR UPDATE, decrements stock, inserts order header & items, applies coupon in one ACID transaction.", font_size=7.0)

    # Row 2: View & Dynamic Aggregation
    set_cell(t_feat.cell(2, 0), "2", font_size=7.0)
    set_cell(t_feat.cell(2, 1), "View & Dynamic Aggregation", font_size=7.0)
    set_cell(t_feat.cell(2, 2), "v_order_total", font_size=7.0)
    set_cell(t_feat.cell(2, 3), "db/schema.sql : 129-138", font_size=6.8)
    set_cell(t_feat.cell(2, 4), "Centralized order financial view joining orders, order_item, and coupon; computes gross, active subtotal, coupon discount, and net payable amount.", font_size=7.0)

    # Row 3: GIN Full-Text & B-Tree Indexes
    set_cell(t_feat.cell(3, 0), "3", font_size=7.0)
    set_cell(t_feat.cell(3, 1), "GIN Full-Text & B-Tree Indexes", font_size=7.0)
    set_cell(t_feat.cell(3, 2), "idx_product_fts,\nidx_listing_product_price,\nuq_one_default_addr", font_size=6.8)
    set_cell(t_feat.cell(3, 3), "db/schema.sql : 33, 124, 126", font_size=6.8)
    set_cell(t_feat.cell(3, 4), "Trigram GIN index yields 11.5x search speedup (12.4ms → 1.08ms); composite B-Tree yields 11.1x speedup; partial index enforces one default address.", font_size=7.0)

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

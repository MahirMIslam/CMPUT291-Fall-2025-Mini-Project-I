import sqlite3
import sys

db_name = sys.argv[1] if len(sys.argv) > 1 else 'test.db'
conn = sqlite3.connect(db_name)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n=== PRODUCT STOCK LEVELS ===")
cursor.execute("""
    SELECT pid, name, stock_count,
           (SELECT COALESCE(SUM(qty), 0) 
            FROM orderlines WHERE pid = products.pid) as sold
    FROM products
    ORDER BY name
""")
products = cursor.fetchall()

for p in products:
    print(f"\n{p['pid']}: {p['name']}")
    print(f"  Current stock: {p['stock_count']}")
    print(f"  Total sold: {p['sold']}")

conn.close()
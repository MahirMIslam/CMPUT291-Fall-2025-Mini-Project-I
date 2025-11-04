import sqlite3
import sys
from datetime import datetime

db_name = sys.argv[1] if len(sys.argv) > 1 else 'test.db'
conn = sqlite3.connect(db_name)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n" + "="*70)
print("PRODUCT UPDATE HISTORY")
print("="*70)

# Get all products with their current values
cursor.execute("""
    SELECT pid, name, category, price, stock_count
    FROM products
    ORDER BY name
""")
products = cursor.fetchall()

print(f"\nTotal Products: {len(products)}")
print("\nCurrent Product Status:")
print("-" * 70)

for p in products:
    print(f"\n{p['pid']}: {p['name']}")
    print(f"  Category: {p['category']}")
    print(f"  Price: ${p['price']:.2f}")
    print(f"  Stock: {p['stock_count']} units")
    
    # Check if product has been sold
    cursor.execute("""
        SELECT COALESCE(SUM(qty), 0) as sold
        FROM orderlines
        WHERE pid = ?
    """, (p['pid'],))
    sold = cursor.fetchone()['sold']
    
    if sold > 0:
        print(f"  Sold: {sold} units")

# Price statistics
cursor.execute("""
    SELECT 
        MIN(price) as min_price,
        MAX(price) as max_price,
        AVG(price) as avg_price
    FROM products
""")
stats = cursor.fetchone()

print("\n" + "="*70)
print("PRICE STATISTICS")
print("="*70)
print(f"Lowest Price: ${stats['min_price']:.2f}")
print(f"Highest Price: ${stats['max_price']:.2f}")
print(f"Average Price: ${stats['avg_price']:.2f}")

# Stock statistics
cursor.execute("""
    SELECT 
        SUM(stock_count) as total_stock,
        AVG(stock_count) as avg_stock
    FROM products
""")
stock_stats = cursor.fetchone()

print("\n" + "="*70)
print("STOCK STATISTICS")
print("="*70)
print(f"Total Stock: {stock_stats['total_stock']} units")
print(f"Average Stock per Product: {stock_stats['avg_stock']:.1f} units")

# Low stock warning
cursor.execute("""
    SELECT pid, name, stock_count
    FROM products
    WHERE stock_count < 15
    ORDER BY stock_count
""")
low_stock = cursor.fetchall()

if low_stock:
    print("\nLOW STOCK WARNING:")
    for p in low_stock:
        print(f"  - {p['name']} ({p['pid']}): Only {p['stock_count']} left!")

print("\n" + "="*70 + "\n")

conn.close()
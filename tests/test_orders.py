import sqlite3
import sys

db_name = sys.argv[1] if len(sys.argv) > 1 else 'test.db'
conn = sqlite3.connect(db_name)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n" + "="*70)
print("ORDER HISTORY TEST")
print("="*70)

# Get all orders with details
cursor.execute("""
    SELECT o.ono, o.cid, c.name, o.odate, o.shipping_address,
           COUNT(ol.lineNo) as items,
           SUM(ol.qty * ol.uprice) as total
    FROM orders o
    LEFT JOIN customers c ON o.cid = c.cid
    LEFT JOIN orderlines ol ON o.ono = ol.ono
    GROUP BY o.ono
    ORDER BY o.odate DESC
""")
orders = cursor.fetchall()

if not orders:
    print("\nNo orders in database. Place some orders first!")
else:
    print(f"\nTotal Orders: {len(orders)}")
    
    for order in orders:
        print(f"\n{'='*70}")
        print(f"Order #{order['ono']} - {order['name']} (CID: {order['cid']})")
        print(f"Date: {order['odate']}")
        print(f"Address: {order['shipping_address']}")
        print(f"Items: {order['items']}")
        print(f"Total: ${order['total']:.2f}")
        
        # Get line items
        cursor.execute("""
            SELECT p.name, ol.qty, ol.uprice, (ol.qty * ol.uprice) as line_total
            FROM orderlines ol
            JOIN products p ON ol.pid = p.pid
            WHERE ol.ono = ?
            ORDER BY ol.lineNo
        """, (order['ono'],))
        lines = cursor.fetchall()
        
        print("\nLine Items:")
        for line in lines:
            print(f"  - {line['name']}: {line['qty']} x ${line['uprice']:.2f} = ${line['line_total']:.2f}")

# Summary statistics
print("\n" + "="*70)
print("STATISTICS")
print("="*70)

cursor.execute("SELECT COUNT(DISTINCT cid) as customers FROM orders")
customer_count = cursor.fetchone()['customers']

cursor.execute("SELECT SUM(ol.qty * ol.uprice) as revenue FROM orderlines ol")
total_revenue = cursor.fetchone()['revenue'] or 0

cursor.execute("SELECT AVG(order_total) as avg_order FROM (SELECT SUM(ol.qty * ol.uprice) as order_total FROM orderlines ol GROUP BY ol.ono)")
avg_order = cursor.fetchone()['avg_order'] or 0

print(f"Total Customers with Orders: {customer_count}")
print(f"Total Orders: {len(orders)}")
print(f"Total Revenue: ${total_revenue:.2f}")
print(f"Average Order Value: ${avg_order:.2f}")
print("="*70 + "\n")

conn.close()
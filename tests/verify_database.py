import sqlite3
import sys

# Connect to database
db_name = sys.argv[1] if len(sys.argv) > 1 else 'test.db'

try:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
except sqlite3.Error as e:
    print(f"Error: Cannot open {db_name}")
    sys.exit(1)

print("\n" + "="*60)
print(f"Checking: {db_name}")
print("="*60)

# Check users
print("\nUSERS:")
cursor.execute("SELECT uid, role FROM users ORDER BY uid")
users = cursor.fetchall()
for user in users:
    print(f"  {user['uid']} - {user['role']}")

# Check customers
print("\nCUSTOMERS:")
cursor.execute("SELECT cid, name, email FROM customers ORDER BY cid")
customers = cursor.fetchall()
for customer in customers:
    print(f"  {customer['cid']} - {customer['name']} ({customer['email']})")

# Check products
print("\nPRODUCTS:")
cursor.execute("SELECT pid, name, price, stock_count FROM products ORDER BY pid")
products = cursor.fetchall()
for p in products:
    print(f"  {p['pid']}: {p['name']} - ${p['price']:.2f} ({p['stock_count']} in stock)")

# Check sessions
print("\nSESSIONS:")
cursor.execute("""
    SELECT s.cid, s.sessionNo, c.name, s.end_time
    FROM sessions s
    LEFT JOIN customers c ON s.cid = c.cid
    ORDER BY s.start_time DESC
    LIMIT 5
""")
sessions = cursor.fetchall()
if sessions:
    for session in sessions:
        status = "Active" if not session['end_time'] else "Ended"
        print(f"  {session['name']} - Session {session['sessionNo']} ({status})")
else:
    print("  No sessions yet")

# Check searches
print("\nRECENT SEARCHES:")
cursor.execute("""
    SELECT c.name, s.query
    FROM search s
    LEFT JOIN customers c ON s.cid = c.cid
    ORDER BY s.ts DESC
    LIMIT 5
""")
searches = cursor.fetchall()
if searches:
    for search in searches:
        print(f"  {search['name']}: '{search['query']}'")
else:
    print("  No searches yet")

# Check product views
print("\nRECENT VIEWS:")
cursor.execute("""
    SELECT c.name, p.name as product
    FROM viewedProduct v
    LEFT JOIN customers c ON v.cid = c.cid
    LEFT JOIN products p ON v.pid = p.pid
    ORDER BY v.ts DESC
    LIMIT 5
""")
views = cursor.fetchall()
if views:
    for view in views:
        print(f"  {view['name']} viewed {view['product']}")
else:
    print("  No views yet")

# Check cart
print("\nCARTS:")
cursor.execute("""
    SELECT c.name, p.name as product, ca.qty, p.price
    FROM cart ca
    LEFT JOIN customers c ON ca.cid = c.cid
    LEFT JOIN products p ON ca.pid = p.pid
    ORDER BY c.name
""")
carts = cursor.fetchall()
if carts:
    current = None
    for item in carts:
        if item['name'] != current:
            print(f"  {item['name']}:")
            current = item['name']
        total = item['qty'] * item['price']
        print(f"    - {item['product']}: {item['qty']} x ${item['price']:.2f} = ${total:.2f}")
else:
    print("  No items in cart")

# Check orders
print("\nORDERS:")
cursor.execute("""
    SELECT o.ono, c.name, o.odate, SUM(ol.qty * ol.uprice) as total
    FROM orders o
    LEFT JOIN customers c ON o.cid = c.cid
    LEFT JOIN orderlines ol ON o.ono = ol.ono
    GROUP BY o.ono
    ORDER BY o.odate DESC
    LIMIT 5
""")
orders = cursor.fetchall()
if orders:
    for order in orders:
        date = order['odate'][:10]
        print(f"  {order['ono']}: {order['name']} - ${order['total']:.2f} ({date})")
else:
    print("  No orders yet")

print("\n" + "="*60)
print(f"Summary: {len(users)} users, {len(customers)} customers, {len(products)} products")
print("="*60 + "\n")

conn.close()
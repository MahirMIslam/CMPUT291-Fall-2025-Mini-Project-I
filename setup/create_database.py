import sqlite3
import os

# Remove old database if it exists
if os.path.exists('test.db'):
    os.remove('test.db')

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

print("\nCreating database...")

# Create all tables
cursor.execute('''
CREATE TABLE users (
    uid TEXT PRIMARY KEY,
    pwd TEXT NOT NULL,
    role TEXT CHECK(role IN ('customer', 'sales'))
)
''')

cursor.execute('''
CREATE TABLE customers (
    cid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)
''')

cursor.execute('''
CREATE TABLE sessions (
    cid TEXT,
    sessionNo INTEGER,
    start_time TEXT,
    end_time TEXT,
    PRIMARY KEY (cid, sessionNo)
)
''')

cursor.execute('''
CREATE TABLE products (
    pid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    stock_count INTEGER,
    descr TEXT
)
''')

cursor.execute('''
CREATE TABLE cart (
    cid TEXT,
    sessionNo INTEGER,
    pid TEXT,
    qty INTEGER,
    PRIMARY KEY (cid, sessionNo, pid)
)
''')

cursor.execute('''
CREATE TABLE orders (
    ono TEXT PRIMARY KEY,
    cid TEXT,
    sessionNo INTEGER,
    odate TEXT,
    shipping_address TEXT
)
''')

cursor.execute('''
CREATE TABLE orderlines (
    ono TEXT,
    lineNo INTEGER,
    pid TEXT,
    qty INTEGER,
    uprice REAL,
    PRIMARY KEY (ono, lineNo)
)
''')

cursor.execute('''
CREATE TABLE viewedProduct (
    cid TEXT,
    sessionNo INTEGER,
    ts TEXT,
    pid TEXT
)
''')

cursor.execute('''
CREATE TABLE search (
    cid TEXT,
    sessionNo INTEGER,
    ts TEXT,
    query TEXT
)
''')

# Insert test users
users = [
    ('1', 'customer123', 'customer'),
    ('2', 'sales456', 'sales'),
    ('100', 'test', 'customer'),
]

for uid, pwd, role in users:
    cursor.execute('INSERT INTO users VALUES (?, ?, ?)', (uid, pwd, role))

# Insert test customers
customers = [
    ('1', 'John Doe', 'john@example.com'),
    ('100', 'Test User', 'test@example.com'),
]

for cid, name, email in customers:
    cursor.execute('INSERT INTO customers VALUES (?, ?, ?)', (cid, name, email))

# Insert sample products
products = [
    ('p1', 'Laptop', 'Electronics', 999.99, 10, 'High-performance laptop with 16GB RAM'),
    ('p2', 'Wireless Mouse', 'Electronics', 29.99, 50, 'Ergonomic wireless mouse'),
    ('p3', 'Mechanical Keyboard', 'Electronics', 79.99, 30, 'RGB mechanical gaming keyboard'),
    ('p4', '27-inch Monitor', 'Electronics', 299.99, 15, '4K LED monitor with HDR'),
    ('p5', 'Noise-Cancelling Headphones', 'Audio', 149.99, 25, 'Premium wireless headphones'),
    ('p6', 'HD Webcam', 'Electronics', 89.99, 20, '1080p webcam with microphone'),
    ('p7', 'USB-C Cable', 'Accessories', 9.99, 100, 'Fast charging USB-C cable'),
    ('p8', 'LED Desk Lamp', 'Furniture', 39.99, 35, 'Adjustable brightness desk lamp'),
    ('p9', 'External SSD', 'Electronics', 129.99, 40, '1TB portable SSD drive'),
    ('p10', 'Gaming Chair', 'Furniture', 249.99, 12, 'Ergonomic gaming chair with lumbar support'),
]

for p in products:
    cursor.execute('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)', p)

conn.commit()
conn.close()

print("✓ Database created: test.db")
print("\nTest accounts:")
print("  Customer: uid=1, password=customer123")
print("  Sales:    uid=2, password=sales456")
print("\nTo verify: python3 tests/verify_database.py")
print("To run app: python3 main.py test.db")
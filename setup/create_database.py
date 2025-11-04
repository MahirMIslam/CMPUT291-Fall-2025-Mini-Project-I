import sys
from pathlib import Path
import sqlite3
import os

# Ensure db_path is specified
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <db_path> [schema_file]")
    sys.exit(1)

db_path = sys.argv[1]  # required
schema_file = Path(__file__).with_name("prj-tables.sql")  # default

# Optional schema_file argument
if len(sys.argv) > 2:
    schema_file = sys.argv[2]

conn = sqlite3.connect(db_path)

conn.execute("PRAGMA foreign_keys = ON")
conn.execute("PRAGMA strict = ON")

cursor = conn.cursor()

print("\nCreating database...")

with open(schema_file, "r", encoding="utf-8") as f:
    conn.executescript(f.read())

conn.commit()

print(f"Database '{db_path}' created successfully from '{schema_file}'.")

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
    (1, 'Laptop', 'Electronics', 999.99, 10, 'High-performance laptop with 16GB RAM'),
    (2, 'Wireless Mouse', 'Electronics', 29.99, 50, 'Ergonomic wireless mouse'),
    (3, 'Mechanical Keyboard', 'Electronics', 79.99, 30, 'RGB mechanical gaming keyboard'),
    (4, '27-inch Monitor', 'Electronics', 299.99, 15, '4K LED monitor with HDR'),
    (5, 'Noise-Cancelling Headphones', 'Audio', 149.99, 25, 'Premium wireless headphones'),
    (6, 'HD Webcam', 'Electronics', 89.99, 20, '1080p webcam with microphone'),
    (7, 'USB-C Cable', 'Accessories', 9.99, 100, 'Fast charging USB-C cable'),
    (8, 'LED Desk Lamp', 'Furniture', 39.99, 35, 'Adjustable brightness desk lamp'),
    (9, 'External SSD', 'Electronics', 129.99, 40, '1TB portable SSD drive'),
    (10, 'Gaming Chair', 'Furniture', 249.99, 12, 'Ergonomic gaming chair with lumbar support'),

    # --- New Products: Laptops (keyword-heavy) ---
    (11, 'Laptop Pro 14', 'Electronics', 1299.99, 8, '14-inch laptop with Intel i7 and RTX 4050 GPU'),
    (12, 'Laptop Air 13', 'Electronics', 899.99, 15, '13-inch lightweight laptop with 16GB RAM and 512GB SSD'),
    (13, 'Laptop Max 16', 'Electronics', 1999.99, 5, '16-inch laptop with Ryzen 9 CPU and RTX 4070 GPU'),
    (14, 'Laptop Student 15', 'Electronics', 699.99, 25, '15-inch laptop with i5 CPU and integrated graphics'),
    (15, 'Laptop Creator 17', 'Electronics', 2199.99, 3, '17-inch laptop with RTX 4080 GPU and 32GB RAM'),
    (16, 'Laptop Budget 14', 'Electronics', 499.99, 30, 'Affordable laptop with 8GB RAM and 256GB SSD'),
    (17, 'Laptop Business 14', 'Electronics', 1149.99, 10, 'Professional laptop with i7 CPU, 16GB RAM, and Thunderbolt 4'),
    (18, 'Laptop Gaming 15', 'Electronics', 1499.99, 6, 'Gaming laptop with Ryzen 7 and RTX 4060 GPU'),
    (19, 'Laptop Compact 12', 'Electronics', 649.99, 20, '12-inch portable laptop for travel and study'),
    (20, 'Laptop Flex 14', 'Electronics', 1099.99, 8, '2-in-1 touchscreen laptop with 16GB RAM and i7 CPU'),

    # --- New Products: SODIMM RAM Kits ---
    (21, 'SODIMM 8GB DDR4 2666MHz', 'Computer Components', 29.99, 50, 'Single 8GB DDR4 SODIMM 2666MHz RAM module'),
    (22, 'SODIMM 16GB DDR4 3200MHz', 'Computer Components', 59.99, 40, 'Single 16GB DDR4 SODIMM 3200MHz RAM module'),
    (23, 'SODIMM 32GB DDR4 3200MHz Kit (2x16GB)', 'Computer Components', 114.99, 30, 'Dual-channel SODIMM RAM kit for laptops'),
    (24, 'SODIMM 64GB DDR4 3200MHz Kit (2x32GB)', 'Computer Components', 229.99, 20, 'High-capacity laptop memory kit for professionals'),
    (25, 'SODIMM 16GB DDR5 4800MHz', 'Computer Components', 79.99, 35, 'Next-gen DDR5 SODIMM for modern laptops'),
    (26, 'SODIMM 32GB DDR5 5600MHz Kit (2x16GB)', 'Computer Components', 149.99, 25, 'High-speed DDR5 laptop memory kit'),
    (27, 'SODIMM 8GB DDR3 1600MHz', 'Computer Components', 24.99, 15, 'Legacy DDR3 SODIMM module for older laptops'),
    (28, 'SODIMM 16GB DDR3 1866MHz Kit (2x8GB)', 'Computer Components', 49.99, 10, 'Dual-channel DDR3 RAM kit for legacy systems'),

    # --- Related Items for Diversity ---
    (29, 'External GPU Enclosure', 'Computer Accessories', 349.99, 10, 'Thunderbolt 3 external GPU enclosure for laptops'),
    (30, 'Laptop Cooling Pad', 'Accessories', 24.99, 40, 'Adjustable laptop cooling pad with dual fans and USB hub'),

     # --- DDR4 SODIMM (Laptop Memory) ---
    (100, 'SODIMM 4GB DDR4 2400MHz', 'Computer Components', 19.99, 60, 'Entry-level DDR4 SODIMM RAM for laptops'),
    (101, 'SODIMM 8GB DDR4 2400MHz', 'Computer Components', 27.99, 55, '8GB DDR4 SODIMM laptop memory module'),
    (102, 'SODIMM 8GB DDR4 3200MHz', 'Computer Components', 31.99, 45, 'High-speed 8GB DDR4 3200MHz SODIMM RAM'),
    (103, 'SODIMM 16GB DDR4 2666MHz Kit (2x8GB)', 'Computer Components', 56.99, 40, 'Dual-channel SODIMM kit for laptops, DDR4 2666MHz'),
    (104, 'SODIMM 32GB DDR4 3600MHz Kit (2x16GB)', 'Computer Components', 129.99, 25, 'High-performance SODIMM RAM kit for gaming laptops'),
    (105, 'SODIMM 64GB DDR4 3600MHz Kit (2x32GB)', 'Computer Components', 239.99, 18, 'Professional DDR4 laptop memory kit for creators'),

    # --- DDR5 SODIMM (Laptop Memory) ---
    (106, 'SODIMM 8GB DDR5 4800MHz', 'Computer Components', 49.99, 50, 'DDR5 4800MHz laptop RAM module'),
    (107, 'SODIMM 16GB DDR5 5200MHz', 'Computer Components', 69.99, 45, 'Fast DDR5 SODIMM laptop RAM with 5200MHz clock'),
    (108, 'SODIMM 32GB DDR5 5600MHz Kit (2x16GB)', 'Computer Components', 149.99, 30, 'Dual-channel DDR5 SODIMM RAM kit for laptops'),
    (109, 'SODIMM 64GB DDR5 6400MHz Kit (2x32GB)', 'Computer Components', 299.99, 20, 'High-speed DDR5 laptop memory kit for professionals'),

    # --- DDR3 SODIMM (Legacy Laptop Memory) ---
    (110, 'SODIMM 4GB DDR3 1333MHz', 'Computer Components', 17.99, 25, 'Legacy DDR3 SODIMM laptop memory'),
    (111, 'SODIMM 8GB DDR3 1600MHz Kit (2x4GB)', 'Computer Components', 34.99, 20, 'Dual-channel DDR3 SODIMM kit for older laptops'),
    (112, 'SODIMM 16GB DDR3 1866MHz Kit (2x8GB)', 'Computer Components', 54.99, 12, 'High-capacity DDR3 SODIMM kit for legacy systems'),

    # --- DDR4 DIMM (Desktop Memory) ---
    (113, 'DIMM 8GB DDR4 2666MHz', 'Computer Components', 29.99, 80, 'Single 8GB DDR4 desktop RAM stick'),
    (114, 'DIMM 16GB DDR4 3200MHz', 'Computer Components', 54.99, 60, 'Single 16GB DDR4 3200MHz desktop RAM'),
    (115, 'DIMM 32GB DDR4 3600MHz Kit (2x16GB)', 'Computer Components', 119.99, 45, 'Dual-channel DDR4 desktop RAM kit for gamers'),
    (116, 'DIMM 64GB DDR4 4000MHz Kit (2x32GB)', 'Computer Components', 239.99, 25, 'High-performance DDR4 RAM kit for workstations'),

    # --- DDR5 DIMM (Desktop Memory) ---
    (117, 'DIMM 16GB DDR5 5200MHz', 'Computer Components', 79.99, 50, 'Next-generation DDR5 5200MHz desktop RAM'),
    (118, 'DIMM 32GB DDR5 6000MHz Kit (2x16GB)', 'Computer Components', 159.99, 40, 'Dual-channel DDR5 RAM kit for high-end PCs'),
    (119, 'DIMM 64GB DDR5 6400MHz Kit (2x32GB)', 'Computer Components', 299.99, 25, 'High-speed DDR5 RAM kit for enthusiasts'),
    (120, 'DIMM 128GB DDR5 7200MHz Kit (4x32GB)', 'Computer Components', 589.99, 10, 'Extreme-performance DDR5 desktop RAM kit for professionals'),
]

for p in products:
    cursor.execute('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)', p)

conn.commit()
conn.close()

print(f"✓ Database created: {db_path}")
print("\nTest accounts:")
print("  Customer: uid=1, password=customer123")
print("  Sales:    uid=2, password=sales456")
print("\nTo verify: python3 tests/verify_database.py")
print(f"To run app: python3 main.py {db_path}")
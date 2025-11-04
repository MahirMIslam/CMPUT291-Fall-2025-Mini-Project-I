import sqlite3
import sys
import getpass
from datetime import datetime, timedelta

class ECommerceSystem:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()
        self.current_user = None
        self.current_role = None
        self.session_no = None
    
    def close(self):
        self.conn.close()
    
    def login(self):
        print("\n=== LOGIN ===")
        uid = input("User ID: ").strip()
        pwd = getpass.getpass("Password: ")
        
        try:
            # Parameterized query prevents SQL injection
            self.cursor.execute(
                "SELECT uid, role FROM users WHERE uid = ? AND pwd = ?",
                (uid, pwd)
            )
            user = self.cursor.fetchone()
            
            if user:
                self.current_user = user['uid']
                self.current_role = user['role']
                self.start_session()
                print(f"\nWelcome! Logged in as {self.current_role}.")
                return True
            else:
                print("Invalid credentials.")
                return False
        except sqlite3.Error as e:
            print(f"Login error: {e}")
            return False
        
    def register(self):
        print("\n=== REGISTRATION ===")
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        pwd = getpass.getpass("Password: ")
        pwd_confirm = getpass.getpass("Confirm Password: ")
        
        if pwd != pwd_confirm:
            print("Passwords do not match.")
            return False
        
        try:
            # Check if email exists
            self.cursor.execute(
                "SELECT email FROM customers WHERE email = ?", (email,)
            )
            if self.cursor.fetchone():
                print("Email already registered.")
                return False
            
            # Generate unique uid
            self.cursor.execute("SELECT MAX(CAST(uid AS INTEGER)) FROM users")
            max_uid = self.cursor.fetchone()[0]
            new_uid = str((max_uid or 0) + 1)
            
            # Generate unique cid
            self.cursor.execute("SELECT MAX(CAST(cid AS INTEGER)) FROM customers")
            max_cid = self.cursor.fetchone()[0]
            new_cid = str((max_cid or 0) + 1)
            
            # Insert into users
            self.cursor.execute(
                "INSERT INTO users (uid, pwd, role) VALUES (?, ?, 'customer')",
                (new_uid, pwd)
            )
            
            # Insert into customers
            self.cursor.execute(
                "INSERT INTO customers (cid, name, email) VALUES (?, ?, ?)",
                (new_cid, name, email)
            )
            
            self.conn.commit()
            print(f"\nRegistration successful! Your User ID is: {new_uid}")
            return True
        except sqlite3.Error as e:
            print(f"Registration error: {e}")
            self.conn.rollback()
            return False

    def start_session(self):
        """Start a new session for the current user"""
        try:
            cid = self.get_customer_id()
            
            # Get next session number
            self.cursor.execute(
                "SELECT MAX(sessionNo) FROM sessions WHERE cid = ?", (cid,)
            )
            max_session = self.cursor.fetchone()[0]
            self.session_no = (max_session or 0) + 1
            
            # Insert new session
            self.cursor.execute(
                "INSERT INTO sessions (cid, sessionNo, start_time) VALUES (?, ?, ?)",
                (cid, self.session_no, datetime.now().isoformat())
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Session error: {e}")
            self.session_no = 1

    def get_customer_id(self):
        """Get customer ID for current user"""
        try:
            # Try to find matching customer by uid
            self.cursor.execute(
                "SELECT cid FROM customers WHERE cid = ?", (self.current_user,)
            )
            result = self.cursor.fetchone()
            if result:
                return result['cid']
            return self.current_user
        except sqlite3.Error:
            return self.current_user

    def logout(self):
        """End session and logout"""
        try:
            if self.session_no:
                cid = self.get_customer_id()
                self.cursor.execute(
                    "UPDATE sessions SET end_time = ? WHERE cid = ? AND sessionNo = ?",
                    (datetime.now().isoformat(), cid, self.session_no)
                )
                self.conn.commit()
        except sqlite3.Error as e:
            print(f"Logout error: {e}")
        
        self.current_user = None
        self.current_role = None
        self.session_no = None
        print("\nLogged out successfully.")

    def customer_menu(self):
        while True:
            print("\n=== CUSTOMER MENU ===")
            print("1. Search for products")
            print("2. View cart")
            print("3. Checkout")
            print("4. My orders")
            print("5. Logout")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.search_products()
            elif choice == '2':
                self.view_cart()
            elif choice == '3':
                self.checkout()
            elif choice == '4':
                self.view_orders()
            elif choice == '5':
                self.logout()
                break
            else:
                print("Invalid choice.")

    def sales_menu(self):
        while True:
            print("\n=== SALES MENU ===")
            print("1. Check/update product")
            print("2. Sales report")
            print("3. Top-selling products")
            print("4. Logout")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.manage_product()
            elif choice == '2':
                self.sales_report()
            elif choice == '3':
                self.top_products()
            elif choice == '4':
                self.logout()
                break
            else:
                print("Invalid choice.")

    def paginate_results(self, items, display_func, action_func, page_size=5):
        """Generic pagination handler"""
        if not items:
            print("\nNo results found.")
            return
        
        total_pages = (len(items) + page_size - 1) // page_size
        current_page = 0
        
        while True:
            # Get current page items
            start = current_page * page_size
            end = min(start + page_size, len(items))
            page_items = items[start:end]
            
            # Display items using provided function
            display_func(page_items)
            
            # Show navigation
            print(f"\nPage {current_page + 1} of {total_pages}")
            options = []
            if current_page > 0:
                options.append("'p' for previous")
            if current_page < total_pages - 1:
                options.append("'n' for next")
            options.append("'s' to select")
            options.append("'b' to go back")
            
            print(" | ".join(options))
            
            choice = input("\nChoice: ").strip().lower()
            
            if choice == 'n' and current_page < total_pages - 1:
                current_page += 1
            elif choice == 'p' and current_page > 0:
                current_page -= 1
            elif choice == 's':
                action_func(items)
            elif choice == 'b':
                break
            else:
                print("Invalid choice.")

    def search_products(self):
        keywords_input = input("\nEnter search keyword(s): ").strip()
        
        if not keywords_input:
            print("Please enter a search term.")
            return
        
        # Split into individual keywords
        keywords = keywords_input.split()
        
        # Record search with original query
        try:
            cid = self.get_customer_id()
            self.cursor.execute(
                "INSERT INTO search (cid, sessionNo, ts, query) VALUES (?, ?, ?, ?)",
                (cid, self.session_no, datetime.now().isoformat(), keywords_input)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Search recording error: {e}")
        
        # Build dynamic query with AND semantics for multiple keywords
        # Each keyword must appear in at least one field (name, descr, or category)
        conditions = []
        params = []
        
        for keyword in keywords:
            keyword_lower = f"%{keyword.lower()}%"
            conditions.append(
                "(LOWER(name) LIKE ? OR LOWER(descr) LIKE ? OR LOWER(category) LIKE ?)"
            )
            params.extend([keyword_lower, keyword_lower, keyword_lower])
        
        # Combine conditions with AND
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT pid, name, category, price, stock_count, descr 
            FROM products 
            WHERE {where_clause}
            ORDER BY name
        """
        
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            if not results:
                print("No products found.")
                return
            
            self.paginate_results(results, self.display_product_summary, 
                                self.handle_product_selection)
        except sqlite3.Error as e:
            print(f"Search error: {e}")

    def display_product_summary(self, products):
        """Display function for pagination"""
        for p in products:
            print(f"\n{'='*50}")
            print(f"ID: {p['pid']} | {p['name']}")
            print(f"Category: {p['category']} | Price: ${p['price']:.2f}")
            print(f"Stock: {p['stock_count']} units")

    def handle_product_selection(self, products):
        """Action function for pagination"""
        pid = input("\nEnter product ID to view details (or 'b' to go back): ").strip()
        if pid.lower() == 'b':
            return
        
        product = next((p for p in products if str(p['pid']) == pid), None)
        if product:
            self.view_product_detail(product)
        else:
            print("Invalid product ID.")

    def view_product_detail(self, product):
        print(f"\n{'='*60}")
        print(f"PRODUCT DETAILS")
        print(f"{'='*60}")
        print(f"ID: {product['pid']}")
        print(f"Name: {product['name']}")
        print(f"Category: {product['category']}")
        print(f"Price: ${product['price']:.2f}")
        print(f"Stock: {product['stock_count']} units available")
        print(f"Description: {product['descr']}")
        print(f"{'='*60}")
        
        # Record view
        try:
            cid = self.get_customer_id()
            self.cursor.execute(
                "INSERT INTO viewedProduct (cid, sessionNo, ts, pid) VALUES (?, ?, ?, ?)",
                (cid, self.session_no, datetime.now().isoformat(), product['pid'])
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"View recording error: {e}")
        
        # Add to cart option
        if product['stock_count'] > 0:
            add = input("\nAdd to cart? (y/n): ").strip().lower()
            if add == 'y':
                self.add_to_cart(product['pid'])
        else:
            print("\nThis product is out of stock.")

    def add_to_cart(self, pid, qty=1):
        try:
            cid = self.get_customer_id()
            
            # Check if already in cart
            self.cursor.execute(
                "SELECT qty FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?",
                (cid, self.session_no, pid)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                new_qty = existing['qty'] + qty
                self.cursor.execute(
                    "UPDATE cart SET qty = ? WHERE cid = ? AND sessionNo = ? AND pid = ?",
                    (new_qty, cid, self.session_no, pid)
                )
                print(f"Updated quantity in cart! (Now: {new_qty})")
            else:
                self.cursor.execute(
                    "INSERT INTO cart (cid, sessionNo, pid, qty) VALUES (?, ?, ?, ?)",
                    (cid, self.session_no, pid, qty)
                )
                print("Added to cart!")
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Cart error: {e}")
            self.conn.rollback()

    def view_cart(self):
        try:
            cid = self.get_customer_id()
            self.cursor.execute(
                """SELECT c.pid, p.name, p.price, c.qty, p.stock_count,
                        (p.price * c.qty) as total
                FROM cart c
                JOIN products p ON c.pid = p.pid
                WHERE c.cid = ? AND c.sessionNo = ?
                ORDER BY p.name""",
                (cid, self.session_no)
            )
            items = self.cursor.fetchall()
            
            if not items:
                print("\nYour cart is empty.")
                return
            
            print("\n" + "="*60)
            print("SHOPPING CART")
            print("="*60)
            
            grand_total = 0
            for item in items:
                print(f"\nProduct ID: {item['pid']}")
                print(f"Name: {item['name']}")
                print(f"Price: ${item['price']:.2f} x {item['qty']} = ${item['total']:.2f}")
                print(f"Available stock: {item['stock_count']}")
                grand_total += item['total']
            
            print(f"\n{'='*60}")
            print(f"GRAND TOTAL: ${grand_total:.2f}")
            print(f"{'='*60}")
            
            # Cart management options
            print("\n1. Update quantity")
            print("2. Remove item")
            print("3. Back to menu")
            
            choice = input("\nChoice: ").strip()
            if choice == '1':
                self.update_cart_qty()
            elif choice == '2':
                self.remove_from_cart()
            elif choice == '3':
                return
            else:
                print("Invalid choice.")
        except sqlite3.Error as e:
            print(f"Cart error: {e}")

    def update_cart_qty(self):
        pid = input("\nEnter product ID: ").strip()
        qty_str = input("Enter new quantity: ").strip()
        
        try:
            qty = int(qty_str)
            if qty <= 0:
                print("Quantity must be positive.")
                return
            
            # Check stock
            self.cursor.execute(
                "SELECT stock_count, name FROM products WHERE pid = ?", (pid,)
            )
            product = self.cursor.fetchone()
            
            if not product:
                print("Product not found.")
                return
            
            if qty > product['stock_count']:
                print(f"Insufficient stock for {product['name']}.")
                print(f"Available: {product['stock_count']} units")
                return
            
            # Update cart
            cid = self.get_customer_id()
            self.cursor.execute(
                "UPDATE cart SET qty = ? WHERE cid = ? AND sessionNo = ? AND pid = ?",
                (qty, cid, self.session_no, pid)
            )
            
            if self.cursor.rowcount > 0:
                self.conn.commit()
                print(f"Quantity updated to {qty}!")
            else:
                print("Product not in cart.")
                
        except ValueError:
            print("Invalid quantity. Please enter a number.")
        except sqlite3.Error as e:
            print(f"Update error: {e}")
            self.conn.rollback()

    def remove_from_cart(self):
        pid = input("\nEnter product ID to remove: ").strip()
        
        try:
            cid = self.get_customer_id()
            
            # Check if item exists in cart first
            self.cursor.execute(
                """SELECT p.name FROM cart c
                JOIN products p ON c.pid = p.pid
                WHERE c.cid = ? AND c.sessionNo = ? AND c.pid = ?""",
                (cid, self.session_no, pid)
            )
            item = self.cursor.fetchone()
            
            if not item:
                print("Product not in cart.")
                return
            
            # Remove item
            self.cursor.execute(
                "DELETE FROM cart WHERE cid = ? AND sessionNo = ? AND pid = ?",
                (cid, self.session_no, pid)
            )
            self.conn.commit()
            print(f"{item['name']} removed from cart!")
            
        except sqlite3.Error as e:
            print(f"Remove error: {e}")
            self.conn.rollback()


    def checkout(self):
        try:
            cid = self.get_customer_id()
            
            # Get cart items
            self.cursor.execute(
                """SELECT c.pid, p.name, p.price, c.qty, p.stock_count
                FROM cart c
                JOIN products p ON c.pid = p.pid
                WHERE c.cid = ? AND c.sessionNo = ?
                ORDER BY p.name""",
                (cid, self.session_no)
            )
            items = self.cursor.fetchall()
            
            if not items:
                print("\nYour cart is empty. Add items before checkout.")
                return
            
            # Validate stock for all items
            stock_issues = []
            for item in items:
                if item['qty'] > item['stock_count']:
                    stock_issues.append(f"  - {item['name']}: Need {item['qty']}, only {item['stock_count']} available")
            
            if stock_issues:
                print("\nCannot proceed with checkout. Stock issues:")
                for issue in stock_issues:
                    print(issue)
                print("\nPlease update your cart quantities.")
                return
            
            # Display order summary
            print("\n" + "="*60)
            print("ORDER SUMMARY")
            print("="*60)
            
            grand_total = 0
            for item in items:
                subtotal = item['price'] * item['qty']
                print(f"\n{item['name']}")
                print(f"  Quantity: {item['qty']} x ${item['price']:.2f} = ${subtotal:.2f}")
                grand_total += subtotal
            
            print(f"\n{'='*60}")
            print(f"TOTAL: ${grand_total:.2f}")
            print(f"{'='*60}")
            
            # Get shipping address
            print("\n")
            address = input("Shipping address: ").strip()
            
            if not address:
                print("Shipping address is required.")
                return
            
            # Confirm order
            print(f"\nTotal amount: ${grand_total:.2f}")
            confirm = input("Confirm order? (yes/no): ").strip().lower()
            
            if confirm not in ['yes', 'y']:
                print("Order cancelled.")
                return
            
            # Generate unique order number
            self.cursor.execute("SELECT MAX(CAST(ono AS INTEGER)) FROM orders")
            max_ono = self.cursor.fetchone()[0]
            ono = str((max_ono or 0) + 1)
            
            # Create order
            self.cursor.execute(
                """INSERT INTO orders (ono, cid, sessionNo, odate, shipping_address)
                VALUES (?, ?, ?, ?, ?)""",
                (ono, cid, self.session_no, datetime.now().date().isoformat(), address)
            )
            
            # Create order lines and update stock
            line_no = 1
            for item in items:
                # Insert order line
                self.cursor.execute(
                    """INSERT INTO orderlines (ono, lineNo, pid, qty, uprice)
                    VALUES (?, ?, ?, ?, ?)""",
                    (ono, line_no, item['pid'], item['qty'], item['price'])
                )
                
                # Update stock
                self.cursor.execute(
                    "UPDATE products SET stock_count = stock_count - ? WHERE pid = ?",
                    (item['qty'], item['pid'])
                )
                
                line_no += 1
            
            # Clear cart
            self.cursor.execute(
                "DELETE FROM cart WHERE cid = ? AND sessionNo = ?",
                (cid, self.session_no)
            )
            
            self.conn.commit()
            
            print("\n" + "="*60)
            print("ORDER PLACED SUCCESSFULLY!")
            print("="*60)
            print(f"Order Number: {ono}")
            print(f"Total: ${grand_total:.2f}")
            print(f"Shipping to: {address}")
            print("\nThank you for your order!")
            
        except sqlite3.Error as e:
            print(f"\nCheckout error: {e}")
            self.conn.rollback()

    def view_orders(self):
        try:
            cid = self.get_customer_id()
            
            # Get all orders for this customer
            self.cursor.execute(
                """SELECT o.ono, o.odate, o.shipping_address,
                        SUM(ol.qty * ol.uprice) as total
                FROM orders o
                JOIN orderlines ol ON o.ono = ol.ono
                WHERE o.cid = ?
                GROUP BY o.ono
                ORDER BY o.odate DESC""",
                (cid,)
            )
            orders = self.cursor.fetchall()
            
            if not orders:
                print("\nYou have no orders yet.")
                return
            
            # Use pagination to display orders
            self.paginate_results(
                orders,
                self.display_order_summary,
                self.handle_order_selection
            )
        except sqlite3.Error as e:
            print(f"Orders error: {e}")

    def display_order_summary(self, orders):
        """Display function for order pagination"""
        print("\n" + "="*60)
        print("YOUR ORDERS")
        print("="*60)
        
        for o in orders:
            print(f"\nOrder #{o['ono']}")
            print(f"Date: {o['odate']}")
            print(f"Total: ${o['total']:.2f}")
            print(f"Shipping: {o['shipping_address']}")
            print("-" * 60)

    def handle_order_selection(self, orders):
        """Action function for order pagination"""
        ono = input("\nEnter order number for details (or 'b' to go back): ").strip()
        if ono.lower() == 'b':
            return
        
        order = next((o for o in orders if str(o['ono']) == ono), None)
        if order:
            self.view_order_detail(ono)
        else:
            print("Invalid order number.")

    def view_order_detail(self, ono):
        try:
            # Get order header
            self.cursor.execute(
                "SELECT ono, odate, shipping_address FROM orders WHERE ono = ?",
                (ono,)
            )
            order = self.cursor.fetchone()
            
            if not order:
                print("Order not found.")
                return
            
            # Get order lines
            self.cursor.execute(
                """SELECT p.name, p.category, ol.qty, ol.uprice,
                        (ol.qty * ol.uprice) as line_total
                FROM orderlines ol
                JOIN products p ON ol.pid = p.pid
                WHERE ol.ono = ?
                ORDER BY ol.lineNo""",
                (ono,)
            )
            lines = self.cursor.fetchall()
            
            # Display order header
            print("\n" + "="*70)
            print(f"ORDER DETAILS - Order #{order['ono']}")
            print("="*70)
            print(f"Order Date: {order['odate']}")
            print(f"Shipping Address: {order['shipping_address']}")
            print("="*70)
            
            # Display line items
            grand_total = 0
            print("\nITEMS:")
            print("-" * 70)
            
            for line in lines:
                print(f"\n{line['name']} ({line['category']})")
                print(f"  Quantity: {line['qty']}")
                print(f"  Unit Price: ${line['uprice']:.2f}")
                print(f"  Line Total: ${line['line_total']:.2f}")
                grand_total += line['line_total']
            
            # Display footer
            print("\n" + "="*70)
            print(f"GRAND TOTAL: ${grand_total:.2f}")
            print("="*70)
            
            input("\nPress Enter to continue...")
            
        except sqlite3.Error as e:
            print(f"Order detail error: {e}")


    def manage_product(self):
        pid = input("\nEnter product ID: ").strip()
        
        if not pid:
            print("Product ID is required.")
            return
        
        try:
            # Get product details
            self.cursor.execute(
                "SELECT * FROM products WHERE pid = ?", (pid,)
            )
            product = self.cursor.fetchone()
            
            if not product:
                print(f"Product '{pid}' not found.")
                return
            
            # Display product details
            print("\n" + "="*60)
            print("PRODUCT INFORMATION")
            print("="*60)
            print(f"ID: {product['pid']}")
            print(f"Name: {product['name']}")
            print(f"Category: {product['category']}")
            print(f"Price: ${product['price']:.2f}")
            print(f"Stock: {product['stock_count']} units")
            print(f"Description: {product['descr']}")
            print("="*60)
            
            # Update options
            print("\n1. Update price")
            print("2. Update stock")
            print("3. Back")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                self.update_product_price(pid, product['name'])
            elif choice == '2':
                self.update_product_stock(pid, product['name'])
            elif choice == '3':
                return
            else:
                print("Invalid choice.")
        
        except sqlite3.Error as e:
            print(f"Product error: {e}")

    def update_product_price(self, pid, product_name):
        """Update product price"""
        new_price_str = input(f"\nEnter new price for {product_name}: $").strip()
        
        try:
            new_price = float(new_price_str)
            
            if new_price <= 0:
                print("Price must be positive.")
                return
            
            # Confirm update
            confirm = input(f"Update price to ${new_price:.2f}? (yes/no): ").strip().lower()
            
            if confirm not in ['yes', 'y']:
                print("Price update cancelled.")
                return
            
            # Update price
            self.cursor.execute(
                "UPDATE products SET price = ? WHERE pid = ?",
                (new_price, pid)
            )
            self.conn.commit()
            
            print(f"Price updated to ${new_price:.2f}!")
            
        except ValueError:
            print("Invalid price. Please enter a number.")
        except sqlite3.Error as e:
            print(f"Update error: {e}")
            self.conn.rollback()

    def update_product_stock(self, pid, product_name):
        """Update product stock"""
        new_stock_str = input(f"\nEnter new stock count for {product_name}: ").strip()
        
        try:
            new_stock = int(new_stock_str)
            
            if new_stock < 0:
                print("Stock must be non-negative.")
                return
            
            # Confirm update
            confirm = input(f"Update stock to {new_stock} units? (yes/no): ").strip().lower()
            
            if confirm not in ['yes', 'y']:
                print("Stock update cancelled.")
                return
            
            # Update stock
            self.cursor.execute(
                "UPDATE products SET stock_count = ? WHERE pid = ?",
                (new_stock, pid)
            )
            self.conn.commit()
            
            print(f"Stock updated to {new_stock} units!")
            
        except ValueError:
            print("Invalid stock count. Please enter a number.")
        except sqlite3.Error as e:
            print(f"Update error: {e}")
            self.conn.rollback()

    def sales_report(self):
        """Generate weekly sales report (last 7 days)"""
        try:
            # Calculate date 7 days ago
            week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
            
            print("\n" + "="*60)
            print("WEEKLY SALES REPORT")
            print(f"Period: Last 7 days (since {week_ago})")
            print("="*60)
            
            # 1. Distinct orders
            self.cursor.execute(
                "SELECT COUNT(DISTINCT ono) as count FROM orders WHERE odate >= ?",
                (week_ago,)
            )
            order_count = self.cursor.fetchone()['count']
            
            # 2. Distinct products sold
            self.cursor.execute(
                """SELECT COUNT(DISTINCT ol.pid) as count
                FROM orderlines ol
                JOIN orders o ON ol.ono = o.ono
                WHERE o.odate >= ?""",
                (week_ago,)
            )
            product_count = self.cursor.fetchone()['count']
            
            # 3. Distinct customers
            self.cursor.execute(
                "SELECT COUNT(DISTINCT cid) as count FROM orders WHERE odate >= ?",
                (week_ago,)
            )
            customer_count = self.cursor.fetchone()['count']
            
            # 4. Total sales
            self.cursor.execute(
                """SELECT COALESCE(SUM(ol.qty * ol.uprice), 0) as total
                FROM orderlines ol
                JOIN orders o ON ol.ono = o.ono
                WHERE o.odate >= ?""",
                (week_ago,)
            )
            total_sales = self.cursor.fetchone()['total']
            
            # 5. Average per customer
            avg_per_customer = total_sales / customer_count if customer_count > 0 else 0
            
            # Display report
            print(f"\nDistinct Orders: {order_count}")
            print(f"Distinct Products Sold: {product_count}")
            print(f"Distinct Customers: {customer_count}")
            print(f"Average per Customer: ${avg_per_customer:.2f}")
            print(f"Total Sales: ${total_sales:.2f}")
            print("="*60)
            
            input("\nPress Enter to continue...")
            
        except sqlite3.Error as e:
            print(f"Report error: {e}")


    def top_products(self):
        """Display top-selling products"""
        try:
            print("\n" + "="*60)
            print("TOP-SELLING PRODUCTS")
            print("="*60)
            
            # Top 3 by distinct orders (with tie handling)
            print("\nTOP 3 BY NUMBER OF ORDERS:")
            print("-" * 60)
            
            # First, get the count of the 3rd ranked product
            self.cursor.execute("""
                SELECT COUNT(DISTINCT ol.ono) as order_count
                FROM products p
                JOIN orderlines ol ON p.pid = ol.pid
                GROUP BY p.pid
                ORDER BY order_count DESC
                LIMIT 1 OFFSET 2
            """)
            third_place_result = self.cursor.fetchone()
            
            if third_place_result:
                third_place_count = third_place_result['order_count']
                
                # Get all products with count >= 3rd place count
                self.cursor.execute("""
                    SELECT p.pid, p.name, p.category, COUNT(DISTINCT ol.ono) as order_count
                    FROM products p
                    JOIN orderlines ol ON p.pid = ol.pid
                    GROUP BY p.pid
                    HAVING order_count >= ?
                    ORDER BY order_count DESC, p.name
                """, (third_place_count,))
                top_orders = self.cursor.fetchall()
            else:
                # Less than 3 products with orders, just get all
                self.cursor.execute("""
                    SELECT p.pid, p.name, p.category, COUNT(DISTINCT ol.ono) as order_count
                    FROM products p
                    JOIN orderlines ol ON p.pid = ol.pid
                    GROUP BY p.pid
                    ORDER BY order_count DESC, p.name
                    LIMIT 3
                """)
                top_orders = self.cursor.fetchall()
            
            if top_orders:
                for i, p in enumerate(top_orders, 1):
                    print(f"{i}. {p['name']} (ID: {p['pid']})")
                    print(f"   Category: {p['category']}")
                    print(f"   Appears in {p['order_count']} order(s)\n")
            else:
                print("   No orders yet.\n")
            
            # Top 3 by views (with tie handling)
            print("TOP 3 BY NUMBER OF VIEWS:")
            print("-" * 60)
            
            # First, get the count of the 3rd ranked product by views
            self.cursor.execute("""
                SELECT COUNT(*) as view_count
                FROM products p
                JOIN viewedProduct vp ON p.pid = vp.pid
                GROUP BY p.pid
                ORDER BY view_count DESC
                LIMIT 1 OFFSET 2
            """)
            third_place_views = self.cursor.fetchone()
            
            if third_place_views:
                third_place_view_count = third_place_views['view_count']
                
                # Get all products with views >= 3rd place count
                self.cursor.execute("""
                    SELECT p.pid, p.name, p.category, COUNT(*) as view_count
                    FROM products p
                    JOIN viewedProduct vp ON p.pid = vp.pid
                    GROUP BY p.pid
                    HAVING view_count >= ?
                    ORDER BY view_count DESC, p.name
                """, (third_place_view_count,))
                top_views = self.cursor.fetchall()
            else:
                # Less than 3 products with views, just get all
                self.cursor.execute("""
                    SELECT p.pid, p.name, p.category, COUNT(*) as view_count
                    FROM products p
                    JOIN viewedProduct vp ON p.pid = vp.pid
                    GROUP BY p.pid
                    ORDER BY view_count DESC, p.name
                    LIMIT 3
                """)
                top_views = self.cursor.fetchall()
            
            if top_views:
                for i, p in enumerate(top_views, 1):
                    print(f"{i}. {p['name']} (ID: {p['pid']})")
                    print(f"   Category: {p['category']}")
                    print(f"   Viewed {p['view_count']} time(s)\n")
            else:
                print("   No product views yet.\n")
            
            print("="*60)
            input("\nPress Enter to continue...")
            
        except sqlite3.Error as e:
            print(f"Top products error: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <database_file>")
        sys.exit(1)
    
    db_name = sys.argv[1]
    system = ECommerceSystem(db_name)
    
    try:
        while True:
            print("\n" + "="*50)
            print("E-COMMERCE SYSTEM")
            print("="*50)
            print("1. Login")
            print("2. Register")
            print("3. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '1':
                if system.login():
                    if system.current_role == 'customer':
                        system.customer_menu()
                    elif system.current_role == 'sales':
                        system.sales_menu()
            elif choice == '2':
                system.register()
            elif choice == '3':
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice.")
    finally:
        system.close()


if __name__ == "__main__":
    main()
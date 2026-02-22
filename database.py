"""
database.py - SQLite database layer for the Smart Inventory Management System.
Handles all CRUD operations for products, stock movements, and sales.
"""

import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.db")


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS products (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL,
        sku             TEXT    NOT NULL UNIQUE,
        category_id     INTEGER,
        price           REAL    NOT NULL DEFAULT 0.0,
        cost_price      REAL    NOT NULL DEFAULT 0.0,
        quantity         INTEGER NOT NULL DEFAULT 0,
        low_stock_threshold INTEGER NOT NULL DEFAULT 10,
        description     TEXT,
        created_at      TEXT    NOT NULL,
        updated_at      TEXT    NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );

    CREATE TABLE IF NOT EXISTS sales (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER NOT NULL,
        quantity_sold    INTEGER NOT NULL,
        sale_price       REAL    NOT NULL,
        total            REAL    NOT NULL,
        sale_date        TEXT    NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS stock_movements (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER NOT NULL,
        movement_type   TEXT    NOT NULL,  -- 'IN' or 'OUT'
        quantity         INTEGER NOT NULL,
        note            TEXT,
        created_at      TEXT    NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # Seed default categories if empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        default_cats = ["Electronics", "Clothing", "Food & Beverages",
                        "Stationery", "Furniture", "Other"]
        cursor.executemany("INSERT INTO categories (name) VALUES (?)",
                           [(c,) for c in default_cats])

    conn.commit()
    conn.close()


# --------------- Category helpers ---------------

def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    conn.close()
    return rows


def add_category(name: str):
    conn = get_connection()
    conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


# --------------- Product CRUD ---------------

def add_product(name, sku, category_id, price, cost_price, quantity,
                low_stock_threshold, description=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("""
        INSERT INTO products
            (name, sku, category_id, price, cost_price, quantity,
             low_stock_threshold, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, sku, category_id, price, cost_price, quantity,
          low_stock_threshold, description, now, now))
    conn.commit()
    conn.close()


def update_product(product_id, name, sku, category_id, price, cost_price,
                   quantity, low_stock_threshold, description=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("""
        UPDATE products SET
            name=?, sku=?, category_id=?, price=?, cost_price=?,
            quantity=?, low_stock_threshold=?, description=?, updated_at=?
        WHERE id=?
    """, (name, sku, category_id, price, cost_price, quantity,
          low_stock_threshold, description, now, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    conn.execute("DELETE FROM sales WHERE product_id=?", (product_id,))
    conn.execute("DELETE FROM stock_movements WHERE product_id=?", (product_id,))
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def get_all_products():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, p.name, p.sku, c.name, p.price, p.cost_price,
               p.quantity, p.low_stock_threshold, p.description,
               p.created_at, p.updated_at, p.category_id
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.name
    """).fetchall()
    conn.close()
    return rows


def search_products(keyword):
    conn = get_connection()
    like = f"%{keyword}%"
    rows = conn.execute("""
        SELECT p.id, p.name, p.sku, c.name, p.price, p.cost_price,
               p.quantity, p.low_stock_threshold, p.description,
               p.created_at, p.updated_at, p.category_id
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.name LIKE ? OR p.sku LIKE ? OR c.name LIKE ?
        ORDER BY p.name
    """, (like, like, like)).fetchall()
    conn.close()
    return rows


def get_low_stock_products():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, p.name, p.sku, c.name, p.price, p.cost_price,
               p.quantity, p.low_stock_threshold
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.quantity <= p.low_stock_threshold
        ORDER BY p.quantity ASC
    """).fetchall()
    conn.close()
    return rows


def get_product_by_id(product_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT p.id, p.name, p.sku, c.name, p.price, p.cost_price,
               p.quantity, p.low_stock_threshold, p.description,
               p.created_at, p.updated_at, p.category_id
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id=?
    """, (product_id,)).fetchone()
    conn.close()
    return row


# --------------- Stock movements ---------------

def add_stock_in(product_id, quantity, note=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("""
        INSERT INTO stock_movements (product_id, movement_type, quantity, note, created_at)
        VALUES (?, 'IN', ?, ?, ?)
    """, (product_id, quantity, note, now))
    conn.execute("UPDATE products SET quantity = quantity + ?, updated_at=? WHERE id=?",
                 (quantity, now, product_id))
    conn.commit()
    conn.close()


def add_stock_out(product_id, quantity, note=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute("""
        INSERT INTO stock_movements (product_id, movement_type, quantity, note, created_at)
        VALUES (?, 'OUT', ?, ?, ?)
    """, (product_id, quantity, note, now))
    conn.execute("UPDATE products SET quantity = quantity - ?, updated_at=? WHERE id=?",
                 (quantity, now, product_id))
    conn.commit()
    conn.close()


# --------------- Sales ---------------

def record_sale(product_id, quantity_sold, sale_price):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = quantity_sold * sale_price
    conn = get_connection()
    conn.execute("""
        INSERT INTO sales (product_id, quantity_sold, sale_price, total, sale_date)
        VALUES (?, ?, ?, ?, ?)
    """, (product_id, quantity_sold, sale_price, total, now))
    conn.execute("UPDATE products SET quantity = quantity - ?, updated_at=? WHERE id=?",
                 (quantity_sold, now, product_id))
    conn.commit()
    conn.close()


def get_sales(start_date=None, end_date=None):
    conn = get_connection()
    query = """
        SELECT s.id, p.name, s.quantity_sold, s.sale_price,
               s.total, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.id
    """
    params = []
    if start_date and end_date:
        query += " WHERE s.sale_date BETWEEN ? AND ?"
        params = [start_date, end_date]
    query += " ORDER BY s.sale_date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_sales_summary():
    """Return daily totals for the last 30 days."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(sale_date) as day, SUM(total) as revenue,
               SUM(quantity_sold) as units
        FROM sales
        WHERE sale_date >= DATE('now', '-30 days')
        GROUP BY DATE(sale_date)
        ORDER BY day
    """).fetchall()
    conn.close()
    return rows


def get_top_products(limit=10):
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, SUM(s.quantity_sold) as total_sold, SUM(s.total) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY revenue DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows


def get_category_sales():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.name, SUM(s.total) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        LEFT JOIN categories c ON p.category_id = c.id
        GROUP BY c.name
        ORDER BY revenue DESC
    """).fetchall()
    conn.close()
    return rows


def get_stock_movements(product_id=None):
    conn = get_connection()
    query = """
        SELECT sm.id, p.name, sm.movement_type, sm.quantity, sm.note, sm.created_at
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.id
    """
    params = []
    if product_id:
        query += " WHERE sm.product_id = ?"
        params = [product_id]
    query += " ORDER BY sm.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

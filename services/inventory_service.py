from database.db_manager import connect

def add_product(name, category, quantity, price, threshold):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, quantity, price, threshold)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, quantity, price, threshold))
    conn.commit()
    conn.close()

def get_all_products():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()
    return data

def delete_product(product_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

def record_sale(product_id, quantity):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO sales (product_id, quantity_sold) VALUES (?, ?)",
        (product_id, quantity)
    )

    cursor.execute(
        "UPDATE products SET quantity = quantity - ? WHERE id=?",
        (quantity, product_id)
    )

    conn.commit()
    conn.close()

def get_low_stock():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE quantity <= threshold
    """)
    data = cursor.fetchall()
    conn.close()
    return data
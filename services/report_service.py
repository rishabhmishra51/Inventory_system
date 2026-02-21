import pandas as pd
from database.db_manager import connect

def export_products_csv():
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    df.to_csv("products_report.csv", index=False)
    conn.close()

def sales_summary():
    conn = connect()
    df = pd.read_sql_query("""
        SELECT p.name, SUM(s.quantity_sold) as total_sold
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
    """, conn)
    conn.close()
    return df
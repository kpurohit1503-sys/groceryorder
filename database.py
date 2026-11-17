import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "grocery_system"),
    )

def initialize_database():
    # Create the database first, then connect to it.
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    cursor = connection.cursor()
    db_name = os.getenv("DB_NAME", "grocery_system")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cursor.close()
    connection.close()

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(120) NOT NULL,
            address TEXT NOT NULL,
            delivery_date DATE NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            item_name VARCHAR(100) NOT NULL,
            quantity DECIMAL(10, 2) NOT NULL,
            unit VARCHAR(30) NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

def _insert_items(cursor, order_id, items):
    for item in items:
        cursor.execute("""
            INSERT INTO order_items
                (order_id, item_name, quantity, unit, unit_price)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_id, item["name"], item["quantity"], item["unit"], item["unit_price"]))

def create_order(customer, address, delivery_date, items):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_name, address, delivery_date)
            VALUES (%s, %s, %s)
        """, (customer, address, delivery_date))
        order_id = cursor.lastrowid
        _insert_items(cursor, order_id, items)
        connection.commit()
        return order_id
    except Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def get_order(order_id):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return None
        cursor.execute("""
            SELECT item_name, quantity, unit, unit_price
            FROM order_items WHERE order_id = %s ORDER BY id
        """, (order_id,))
        order["items"] = cursor.fetchall()
        order["total"] = sum(float(i["quantity"]) * float(i["unit_price"]) for i in order["items"])
        return order
    finally:
        connection.close()

def list_orders():
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.id, o.customer_name, o.delivery_date, o.status,
                   COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.id
            GROUP BY o.id, o.customer_name, o.delivery_date, o.status
            ORDER BY o.id DESC
        """)
        rows = cursor.fetchall()
        for row in rows:
            row["total"] = float(row["total"])
        return rows
    finally:
        connection.close()

def update_order(order_id, customer, address, delivery_date, items=None):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE orders
            SET customer_name=%s, address=%s, delivery_date=%s
            WHERE id=%s
        """, (customer, address, delivery_date, order_id))
        if cursor.rowcount == 0:
            connection.rollback()
            return False
        if items is not None:
            cursor.execute("DELETE FROM order_items WHERE order_id=%s", (order_id,))
            _insert_items(cursor, order_id, items)
        connection.commit()
        return True
    except Error:
        connection.rollback()
        raise
    finally:
        connection.close()

def delete_order(order_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM orders WHERE id=%s", (order_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()

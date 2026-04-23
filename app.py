from flask import Flask, render_template, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '87654321'),
    'database': os.getenv('MYSQL_DATABASE', 'price_monitor')
}

app = Flask(__name__)

def get_price_history(product_name, limit=30):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT price, check_time 
        FROM price_history 
        WHERE product_name = %s 
        ORDER BY check_time DESC 
        LIMIT %s
    """
    cursor.execute(query, (product_name, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(reversed(rows))

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/prices')
def api_prices():
    product_name = "A Light in the Attic"
    history = get_price_history(product_name)
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True)
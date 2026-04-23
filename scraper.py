import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import os
import re
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', '87654321'),
    'database': os.getenv('MYSQL_DATABASE', 'price_monitor')
}

MAILTRAP_CONFIG = {
    'host': os.getenv('MAILTRAP_HOST'),
    'port': int(os.getenv('MAILTRAP_PORT', 2525)),
    'user': os.getenv('MAILTRAP_USER'),
    'password': os.getenv('MAILTRAP_PASSWORD')
}

def get_price_from_url(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Multiple selectors
        price_selectors = [
            ('p', 'price_color'),
            ('span', 'price'),
            ('span', 'priceblock_ourprice'),
            ('span', 'a-price-whole'),
            ('div', 'product-price'),
            ('meta', {'itemprop': 'price'}),
        ]
        
        price_text = None
        for tag, attr in price_selectors:
            if isinstance(attr, dict):
                elem = soup.find(tag, attr)
            else:
                elem = soup.find(tag, class_=attr)
            if elem:
                price_text = elem.get_text(strip=True)
                break
        
        if not price_text:
            text = soup.get_text()
            match = re.search(r'[£$€]\s*(\d+(?:\.\d{2})?)', text)
            if match:
                price_text = match.group(0)
        
        if not price_text:
            return None
        
        match = re.search(r'(\d+(?:\.\d{2})?)', price_text)
        return float(match.group(1)) if match else None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_price_to_db(product_name, price, currency, url):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "INSERT INTO price_history (product_name, price, currency, url, check_time) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (product_name, price, currency, url, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved: {product_name} = {currency}{price}")

def get_last_price(product_name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "SELECT price, check_time FROM price_history WHERE product_name = %s ORDER BY check_time DESC LIMIT 1"
    cursor.execute(query, (product_name,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        print(f"DEBUG: last price = {row[0]}, timestamp = {row[1]}")
        return row[0]
    else:
        print("DEBUG: no previous price found")
        return None

def check_price_drop(product_name, current_price, threshold_percent=10):
    last_price = get_last_price(product_name)
    if last_price is None:
        return False, None, None
    last_price = float(last_price)  # convert Decimal to float
    current_price = float(current_price)
    if last_price <= current_price:
        return False, last_price, 0
    drop_percent = (last_price - current_price) / last_price * 100
    return (drop_percent >= threshold_percent, last_price, drop_percent)

def send_mailtrap_alert(product_name, old_price, new_price, url, percent_drop):
    if not all(MAILTRAP_CONFIG.values()):
        print("Mailtrap credentials missing.")
        return
    msg = EmailMessage()
    msg.set_content(f"Price dropped on {product_name}!\nOld: ${old_price:.2f}\nNew: ${new_price:.2f}\nDrop: {percent_drop:.1f}%\nURL: {url}")
    msg['Subject'] = f"💰 Price Drop Alert: {product_name}"
    msg['From'] = 'monitor@example.com'
    msg['To'] = 'client@example.com'
    try:
        with smtplib.SMTP(MAILTRAP_CONFIG['host'], MAILTRAP_CONFIG['port']) as smtp:
            smtp.starttls()
            smtp.login(MAILTRAP_CONFIG['user'], MAILTRAP_CONFIG['password'])
            smtp.send_message(msg)
        print("✅ Alert sent to Mailtrap")
    except Exception as e:
        print(f"Email failed: {e}")

def main():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    name = "A Light in the Attic"
    currency = "$"  # will be overridden by actual symbol, but fine
    
    price = get_price_from_url(url)
    if price is None:
        print("Could not scrape price.")
        return
    
    print(f"Price: {price}")
    save_price_to_db(name, price, currency, url)
    
    dropped, old, pct = check_price_drop(name, price, 10)
    if dropped:
        print(f"Drop from {old} to {price} ({pct:.1f}%)")
        send_mailtrap_alert(name, old, price, url, pct)
    else:
        print("No significant drop")

if __name__ == "__main__":
    main()
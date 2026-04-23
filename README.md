Price Monitor – Automated Web Scraper with Email Alerts & Dashboard

## DASHBOARD
screenshots\sc3.JPG

## MESSAGE RECIEVING
screenshots\sc1.JPG
screenshots\sc2.JPG

## DATABASE INTERACTION
screenshots\sc4.JPG

## BASH INTERACTION
screenshots\sc5.JPG






What it does
This tool automatically monitors product prices from any website. When a price drops significantly (e.g., >10%), it sends an instant email alert (via Mailtrap) and displays the price history on a live dashboard.

## Features
- **Web Scraping** – extracts price from any product page.
- **Database** – stores price history in MySQL.
- **Email Alerts** – sends alerts to Mailtrap (can be replaced with real SMTP).
- **Live Dashboard** – Flask + Chart.js shows price trends.
- **Automation** – scheduled daily runs (local cron or PythonAnywhere tasks).

## Tech Stack
- Python 3.8+
- BeautifulSoup, Requests
- MySQL
- Flask, Chart.js
- Mailtrap (SMTP testing)

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/yeabsira12/price-monitor.git
   cd price-monitor
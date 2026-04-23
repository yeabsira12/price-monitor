import schedule
import time
from scraper import main

schedule.every().day.at("09:00").do(main)

print("🕒 Scheduler started. Will run daily at 9:00 AM.")
while True:
    schedule.run_pending()
    time.sleep(60)
from datetime import datetime


today = datetime.now()
date_string = f"{today.year}.{today.month}.{today.day}"

CONFIG = {
    "scraper_base_url": "https://statusinvest.com.br/fundos-imobiliarios/",
    "request_header": {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/91.0.4472.124 Safari/537.36'
    },
    "firebase_key_path": "firebase-admin-key.json",
    "log_file": f"{date_string}_scraping.log",
    "counter_file": "counters_frequency.csv",
    "sender_email": "testaroo17.gmail.com",
    "recipient_email": "gugagalvao@live.com"
}
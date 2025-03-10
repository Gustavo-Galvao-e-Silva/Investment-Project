import time
from typing import List
import random
from config import CONFIG
from logger import logger
from status_invest_scraper import FundoScraper, FundoImobiliario, ScraperError
from firebase_handling import initialize_firebase
from db_handling import update_database


def main():
    try:
        # Load ticker list (consider moving this to a separate file or database)
        with open('tickers.txt', 'r') as f:
            tickers = [line.strip().lower() for line in f if line.strip()]

        # Initialize components
        db = initialize_firebase()
        scraper = FundoScraper()

        # Run update
        update_database(tickers, scraper, db)

    except Exception as e:
        logger.critical(f"Fatal error in main process: {e}", exc_info=True)


if __name__ == "__main__":
    main()

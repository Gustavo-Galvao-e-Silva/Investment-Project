import firebase_admin
from firebase_admin import credentials, firestore
from status_invest_scraper import Scraper, FundoImobiliario, ScraperError
import time
import logging
from typing import List, Dict, Any
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraping.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        cred = credentials.Certificate("firebase-admin-key.json")
        app = firebase_admin.initialize_app(cred)
        return firestore.client(app)
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


def update_database(tickers: List[str], scraper: Scraper, db: firestore.Client) -> None:
    """
    Update Firebase with data for all tickers

    Args:
        tickers: List of ticker symbols to process
        scraper: Initialized Scraper instance
        db: Firestore database client
    """
    success_count = 0
    error_count = 0

    for i, ticker in enumerate(tickers):
        try:
            # Log progress
            logger.info(f"Processing {ticker} ({i + 1}/{len(tickers)})")

            # Create FundoImobiliario instance and scrape data
            fundo = FundoImobiliario(ticker)

            try:
                scraper.scrape_payment_data(fundo)
            except ScraperError as se:
                logger.warning(f"Could not scrape {ticker}: {se}. Skipping to next ticker.")
                error_count += 1
                continue
            except Exception as e:
                logger.error(f"Unexpected error scraping {ticker}: {e}")
                error_count += 1
                continue

            data = fundo.get_payment_data()

            # Add timestamp and metadata
            data["updated_at"] = firestore.SERVER_TIMESTAMP
            data["ticker"] = ticker.upper()

            # Skip if no meaningful data was retrieved
            if not data.get("payment_amount") and not data.get("unit_price"):
                logger.warning(f"No meaningful data retrieved for {ticker}")
                error_count += 1
                continue

            # Update database
            db.collection("fundos").document(ticker.lower()).set(
                data, merge=True
            )
            success_count += 1

        except Exception as e:
            logger.error(f"Unexpected error processing {ticker}: {e}", exc_info=True)
            error_count += 1

        finally:
            # Always sleep between requests, regardless of success or failure
            sleep_time = 3 + random.uniform(0, 4)
            time.sleep(sleep_time)

    logger.info(f"Update completed. Success: {success_count}, Errors: {error_count}")


def main():
    try:
        # Load ticker list (consider moving this to a separate file or database)
        with open('tickers.txt', 'r') as f:
            tickers = [line.strip().lower() for line in f if line.strip()]

        # Initialize components
        db = initialize_firebase()
        scraper = Scraper()

        # Run update
        update_database(tickers, scraper, db)

    except Exception as e:
        logger.critical(f"Fatal error in main process: {e}", exc_info=True)


if __name__ == "__main__":
    main()
from firebase_admin import firestore
from typing import List, Dict
import random
import time
from logger import logger
from status_invest_scraper import FundoScraper, FundoImobiliario
from data_tracker import write_counters_to_csv


def update_database(tickers: List[str], scraper: FundoScraper, db: firestore.Client) -> None:
    """Update Firebase with data for all tickers"""
    success_count = 0
    error_count = 0
    no_meaningful_update_counter = 0

    for i, ticker in enumerate(tickers):
        try:
            hasUpdatedData = True
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
            if not new_data_is_meaningful(data):
                logger.warning(f"No meaningful data retrieved for {ticker}")
                no_meaningful_update_counter += 1
                hasUpdatedData = False

            # Update database
            db.collection("fundos").document(ticker.lower()).set(data, merge=True)
            if hasUpdatedData:
                success_count += 1

        except Exception as e:
            logger.error(f"Unexpected error processing {ticker}: {e}", exc_info=True)
            error_count += 1

        finally:
            # Always sleep between requests, regardless of success or failure
            sleep_time = 3 + random.uniform(0, 4)
            time.sleep(sleep_time)

    logger.info(f"Update completed. Meaningful data: {success_count}, Errors: {error_count}, No meaningful data retrieved: {no_meaningful_update_counter}")
    write_counters_to_csv(success_count, error_count, no_meaningful_update_counter)


def new_data_is_meaningful(data: Dict) -> bool:
    return data["payment_amount"] != '-' and data["base_date"] != '-' and data["payment_date"] != '-'
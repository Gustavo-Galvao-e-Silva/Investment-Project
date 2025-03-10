import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from config import CONFIG


class ScraperError(Exception):
    pass


class FundoImobiliario:
    def __init__(self, ticker: str):
        self._ticker = ticker
        self._url = f"{CONFIG["scraper_base_url"]}{ticker}"
        self._payment_data = {"base_date": "", "payment_date": "", "payment_amount": "", "unit_price": ""}

    def get_payment_data(self) -> Dict[str, Any]:
        return self._payment_data

    def set_payment_data(self, payment_data: Dict[str, Any]) -> None:
        self._payment_data.update(payment_data)

    @property
    def url(self) -> str:
        return self._url

    @property
    def ticker(self) -> str:
        return self._ticker

class FundoScraper:
    def __init__(self):
        self._logger = self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def _get_html(self, url: str) -> str:
        try:
            headers = CONFIG["request_header"]

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return response.text

        except requests.RequestException as e:
            self._logger.error(f"Request failed: {e}")
            raise ScraperError(f"Failed to fetch URL: {url}") from e

    def scrape_payment_data(self, fundo: FundoImobiliario) -> None:
        try:
            html = self._get_html(fundo.url)

            soup = BeautifulSoup(html, 'html.parser')
            #Might transfer these classes to config file
            date_elements = soup.find_all(class_="sub-value fs-4 lh-3")
            amount_elements = soup.find_all(class_="value d-inline-block fs-5 fw-900")
            price_elements = soup.find_all(class_="value")

            if not date_elements or len(date_elements) < 2:
                self._logger.warning(f"Unable to retrieve base and payment dates for FII: {fundo.ticker}")

            if not amount_elements or len(amount_elements) < 2:
                self._logger.warning(f"Unable to retrieve dividend amounts for FII: {fundo.ticker}")

            if not price_elements:
                self._logger.warning(f"Unable to retrieve current value for FII: {fundo.ticker}")

            payment_data = {}

            if date_elements and len(date_elements) >= 2:
                payment_data["base_date"] = date_elements[-2].text.strip()
                payment_data["payment_date"] = date_elements[-1].text.strip()

            if amount_elements and len(amount_elements) >= 1:
                payment_data["payment_amount"] = amount_elements[-1].text.strip().replace(",", ".")

            if price_elements and len(price_elements) >= 1:
                payment_data["unit_price"] = price_elements[0].text.strip().replace(",", ".")

            fundo.set_payment_data(payment_data)

        except Exception as e:
            self._logger.error(f"Error parsing HTML: {e}")


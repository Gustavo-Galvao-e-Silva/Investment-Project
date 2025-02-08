import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional

class ScraperError(Exception): #Adicionar error handling mais complexo depois
    pass

class Scraper:
    def __init__(self, ticker: str):
        self._url = f"https://statusinvest.com.br/fundos-imobiliarios/{ticker}"
        self._logger = self._setup_logging()
        self._payment_data = {"base_date": "", "payment_date": "", "payment_amount": "", "unit_price": ""}

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def _get_html(self) -> str:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

            response = requests.get(self._url, headers=headers)
            response.raise_for_status()

            return response.text

        except requests.RequestException as e:
            self._logger.error(f"Request failed: {e}")
            raise ScraperError(f"Failed to fetch URL: {self._url}") from e

    def _set_payment_data(self):
        try:
            html = self._get_html()

            soup = BeautifulSoup(html, 'html.parser')
            date_elements = soup.find_all(class_="sub-value fs-4 lh-3")
            amount_elements = soup.find_all(class_="value d-inline-block fs-5 fw-900")
            price_elements = soup.find_all(class_="value")

            if not date_elements or len(date_elements) < 2:
                self._logger.warning("Unable to retrieve base and payment dates")

            if not amount_elements or len(amount_elements) < 2:
                self._logger.warning("Unable to retrieve dividend amounts")

            if not price_elements:
                self._logger.warning("Unable to retrieve current value")

            base_date_text = date_elements[-2].text.strip()
            payment_date_text = date_elements[-1].text.strip()
            payment_amount_value = amount_elements[-1].text.strip().replace(",", ".")
            price_value = price_elements[0].text.strip().replace(",", ".")


            self._payment_data["base_date"] = base_date_text
            self._payment_data["payment_date"] = payment_date_text
            self._payment_data["payment_amount"] = payment_amount_value
            self._payment_data["unit_price"] = price_value

        except Exception as e:
            self._logger.error(f"Error parsing HTML: {e}")

    def get_payment_data(self):
        self._set_payment_data()
        return self._payment_data

from datetime import datetime
import csv
from logger import logger
from config import CONFIG


def write_counters_to_csv(success_count: int, error_count: int, no_meaningful_update_counter: int) -> None:
    try:
        file_name = CONFIG["counter_file"]
        date_string = get_date()
        if not data_from_date_is_meaningful(no_meaningful_update_counter):
            logger.info(f"No meaningful update on {date_string}")
        with open(file_name, 'a', newline='') as csvfile:
            field_names = ["Date", "Success", "Errors", "No Updates"]
            row = {"Date": date_string, "Success": success_count, "Errors": error_count, "No Updates": no_meaningful_update_counter}
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writerow(row)

    except Exception as e:
        logger.error(f"Failed to write counters to {file_name}: {str(e)}")


def get_date() -> str:
    today = datetime.now()
    return f"{today.year}/{today.month}/{today.day}"


def data_from_date_is_meaningful(no_meaningful_update_counter: int) -> bool:
    return not no_meaningful_update_counter


# ETL Script to fetch currency conversion rates and insert them into a MySQL database
import requests
import json
import mysql.connector
import logging
from datetime import datetime
import time
from requests.exceptions import RequestException
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(filename='logs/etl.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'currency_rates'  # Replace with your database name
}

# List of base currencies to fetch data for
base_currencies = ['USD', 'EUR', 'INR']

def fetch_and_insert_conversion_rates():
    try:
        # Connect to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Loop through each base currency
        for base_currency in base_currencies:
            url = f'https://www.floatrates.com/daily/{base_currency.lower()}.json'

            # Fetch the exchange rate data with retry mechanism
            retries = 3
            for attempt in range(retries):
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception for bad status codes
                    data = response.json()
                    break  # Break out of the retry loop if the request is successful
                except RequestException as e:
                    logging.error(f"Request failed for {base_currency} on attempt {attempt + 1}: {e}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff (wait time increases with each attempt)
                    else:
                        logging.error(f"Max retries reached for {base_currency}. Skipping this currency.")
                        continue  # Skip this base currency if all retries fail

            # Loop through the data and insert it into the database
            for target_currency, rate_info in data.items():
                if base_currency != target_currency:
                    rate = rate_info.get('rate')
                    inverse_rate = rate_info.get('inverseRate', None)
                    # Use UTC date
                    date = datetime.now(timezone.utc).date()

                    # Insert base -> target currency with ON DUPLICATE KEY UPDATE to avoid duplicates
                    insert_query = """
                        INSERT INTO conversion_rates (base_currency, target_currency, rate, date)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE rate = VALUES(rate)
                    """
                    cursor.execute(insert_query, (base_currency, target_currency, rate, date))
                    logging.info(f"Inserted {base_currency} to {target_currency} rate of {rate} on {date}.")

                    # Insert target -> base currency (reverse rate) with ON DUPLICATE KEY UPDATE
                    if inverse_rate:
                        insert_query_inverse = """
                            INSERT INTO conversion_rates (base_currency, target_currency, rate, date)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE rate = VALUES(rate)
                        """
                        cursor.execute(insert_query_inverse, (target_currency, base_currency, inverse_rate, date))
                        logging.info(f"Inserted {target_currency} to {base_currency} rate of {inverse_rate} on {date}.")

        # Commit changes
        connection.commit()
        logging.info("ETL Job Completed Successfully")

    except mysql.connector.Error as err:
        logging.error(f"Database connection failed: {err}")
    except RequestException as err:
        logging.error(f"Request failed: {err}")
    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()

# Main function to run the ETL job
if __name__ == "__main__":
    logging.info("ETL Job Started")
    fetch_and_insert_conversion_rates()

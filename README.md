# Currency Conversion Report

This project is a web application that provides a 7-day currency conversion report. The app fetches daily exchange rates from the FloatRates API, stores them in a MySQL database, and allows the user to generate a report with a chart and the biggest currency rate change.

---

## 🚀 Features
- Fetches the latest exchange rates from the FloatRates API and stores them in a MySQL database.
- Displays a line chart of conversion rates for the last 7 days between selected base and target currencies.
- Allows users to select a currency pair (USD ↔ EUR, EUR ↔ INR, INR ↔ USD).
- Supports date selection for generating reports for any specific date (defaults to today).
- Displays the biggest rate change (max and min values) between the selected currencies.

---

## ⚙️ Prerequisites

To get started, make sure you have the following installed:

- **Python 3.x** (Make sure `pip` is also installed with Python)
- **MySQL** (or MariaDB)
- **Flask**
- **Matplotlib**
- **MySQL Connector for Python**

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/currency-conversion-report.git
cd currency-conversion-report

# 💱 Currency Conversion Reporting App

This project is a full-stack Python application that performs ETL on foreign exchange rates, stores them in a MySQL database, and provides a web-based interface for generating a rolling 7-day currency conversion report.

---

## 🚀 Features

- ✅ Daily ETL job fetching live exchange rates from [FloatRates](https://www.floatrates.com/json-feeds.html)
- ✅ Converts and stores exchange rates in a MySQL database
- ✅ Prevents duplicate entries using SQL constraints
- ✅ Flask-based web app to visualize 7-day rolling currency rate trends
- ✅ Select base/target currency and reporting date dynamically
- ✅ Displays biggest percentage rate change in the 7-day window
- ✅ Clean logging and retry mechanism for reliability

---

## 📦 Tech Stack

- **Python 3**
- **Flask**
- **MySQL**
- **Matplotlib**
- **Requests**
- **Jinja2 Templates**
- **Logging**

---

## ⚙️ Prerequisites

Make sure you have the following installed:

- Python 3.x and `pip`
- MySQL Server (or MariaDB)
- Git

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/currency-conversion-report.git
cd currency-conversion-report

2. Create and Activate a Virtual Environment

python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate

3. Install Python Dependencies

pip install -r requirements.txt
If you don't have requirements.txt, create one with:
pip install flask mysql-connector-python matplotlib requests
pip freeze > requirements.txt

4. Set Up the MySQL Database
Log into MySQL and run the schema file:

mysql -u root -p < create_tables.sql
This creates the database currency_rates and the conversion_rates table.

5. Configure Database Credentials
In both etl_script.py and app.py, update the database configuration:

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',          # ← Replace with your actual MySQL password
    'database': 'currency_rates'
}

6. Run the ETL Job
This script fetches daily exchange rates and loads them into the database. Run it manually (or later via a cron job):
python etl_script.py

Log file will be created at logs/etl.log.

7. Start the Web App

python app.py
Visit: http://localhost:5000


🖥️ Using the Web App
On the homepage, you'll see:

A form to select:

Base Currency (USD, EUR, INR)

Target Currency

Report Date (defaults to today)

A line chart of conversion rates for the last 7 days

A summary box showing the biggest % change in rates


# 📁 Project Structure

currency-conversion-report/
│
├── app.py                # Flask app to serve reports
├── etl_script.py         # Fetch and load daily currency data
├── create_tables.sql     # SQL to create schema
├── requirements.txt      # Python package list
├── logs/
│   └── etl.log           # Log file for ETL job
├── templates/
│   └── index.html        # Flask HTML template



📌 Notes
The ETL script runs manually for now — to automate, schedule it with cron (Linux/Mac) or Task Scheduler (Windows).

The app uses UTC date/time for consistency.

Avoid reloading the same rates due to the UNIQUE constraint on (base_currency, target_currency, date).

You can extend the app to support more currencies or better UI/UX styling.

✅ Quick Copy Commands
Clone, install, and run everything:

git clone https://github.com/your-username/currency-conversion-report.git
cd currency-conversion-report
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mysql -u root -p < create_tables.sql
python etl_script.py
python app.py

Then open http://localhost:5000 in your browser.



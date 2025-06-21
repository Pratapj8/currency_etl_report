# Import Flask to create the web app
from flask import Flask, render_template, request, send_file

# MySQL connector to connect and interact with the MySQL database
import mysql.connector
from mysql.connector import pooling

# matplotlib to create graphs or plots
import matplotlib

# BytesIO lets us handle file-like data in memory (useful for images/plots)
from io import BytesIO

# base64 is used to convert binary data (like images) into text for display in HTML
import base64

# This makes sure matplotlib works even without a GUI (e.g., on a server)
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt

# Import datetime to work with dates and times
from datetime import datetime

# Import logging to create log messages for debugging or tracking
import logging

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# MySQL database connection details
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'currency_rates'  # Replace with your database name
}

# Ensure logs directory exists before setting up logging
import os
os.makedirs('logs', exist_ok=True)

# Setup logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Fetch the last 7 days of conversion rates
def fetch_rolling_7_day_data(base_currency, target_currency, report_date):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, rate
            FROM conversion_rates
            WHERE base_currency = %s AND target_currency = %s
            AND date BETWEEN %s - INTERVAL 6 DAY AND %s
            ORDER BY date
        """, (base_currency, target_currency, report_date, report_date))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except mysql.connector.Error as e:
        logging.error(f"Database query error while fetching data for {base_currency} -> {target_currency}: {e}")
        return []

# Generate a line chart for the conversion rates
def generate_chart(data):
    try:
        dates = [item[0] for item in data]
        rates = [item[1] for item in data]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, rates, marker='o', linestyle='-', color='b')
        plt.title("Rolling 7-Day Conversion Rates")
        plt.xlabel("Date")
        plt.ylabel("Conversion Rate")

        # Rotate and format date labels on x-axis
        # Ensure all dates are datetime.date objects
        formatted_dates = []
        for date in dates:
            if isinstance(date, str):
                try:
                    formatted_dates.append(datetime.strptime(date, "%Y-%m-%d").date())
                except ValueError:
                    formatted_dates.append(date)
            else:
                formatted_dates.append(date)
        plt.xticks(
            formatted_dates, 
            [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d) for d in formatted_dates],  # Format the date as YYYY-MM-DD
            rotation=45,  # Rotate by 45 degrees
            ha='right'  # Align the labels to the right for better readability
        )

        # Save the plot to a BytesIO object and encode it to base64 for display in HTML
        img = BytesIO()
        plt.tight_layout()  # Ensure everything fits nicely, especially the x-axis labels
        plt.savefig(img, format='png')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
        return chart_url, img
    except Exception as e:
        logging.error(f"Error generating chart: {e}")
        return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default values
    base_currency = 'USD'
    target_currency = 'EUR'
    report_date = datetime.today().date()
    biggest_change = None  # Ensure variable is always defined

    if request.method == 'POST':
        base_currency = request.form.get('base_currency')
        target_currency = request.form.get('target_currency')
        report_date = request.form.get('report_date')
        if report_date:
            try:
                report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            except ValueError:
                report_date = datetime.today().date()

    # Fetch rolling 7-day data
    data = fetch_rolling_7_day_data(base_currency, target_currency, report_date)

    if data:
        chart_url, img = generate_chart(data)
        # Calculate biggest change (max-min) if data is available
        try:
            rates = [item[1] for item in data]
            if rates:
                biggest_change = max(rates) - min(rates)
        except Exception as e:
            logging.error(f"Error calculating biggest change: {e}")
    else:
        chart_url = None
        img = None
        biggest_change = None

    return render_template(
        'index.html',
        chart_url=chart_url,
        biggest_change=biggest_change,
        selected_base=base_currency,
        selected_target=target_currency,
        selected_date=report_date.strftime('%Y-%m-%d')
    )

@app.route('/download-chart', methods=['POST'])
def download_chart():
    base_currency = request.form.get('base_currency', 'USD')
    target_currency = request.form.get('target_currency', 'EUR')
    date_str = request.form.get('report_date')
    report_date = datetime.today().date()
    if date_str:
        try:
            report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    # Fetch rolling 7-day data
    data = fetch_rolling_7_day_data(base_currency, target_currency, report_date)

    if not data:
        logging.warning(f"No data available for {base_currency} -> {target_currency} on {report_date}")
        return "No data available", 404

    # Generate chart
    chart_url, img = generate_chart(data)

    if not img:
        return "Error generating chart", 500

    # Send the chart as a downloadable PNG file
    return send_file(img, mimetype='image/png', as_attachment=True, download_name='currency_chart.png')

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode)

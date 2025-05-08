from flask import Flask, render_template, request, send_file
import mysql.connector
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib
from datetime import datetime
import logging

# Use the 'Agg' backend for non-interactive plotting
matplotlib.use('Agg')  

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'currency_rates'  # Replace with your database name
}

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
        plt.xticks(
            dates, 
            [date.strftime('%Y-%m-%d') for date in dates],  # Format the date as YYYY-MM-DD
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

    if request.method == 'POST':
        base_currency = request.form.get('base_currency')
        target_currency = request.form.get('target_currency')
        report_date = request.form.get('report_date')
        if report_date:
            report_date = datetime.strptime(report_date, "%Y-%m-%d").date()

    # Fetch rolling 7-day data
    data = fetch_rolling_7_day_data(base_currency, target_currency, report_date)

    if data:
        chart_url, img = generate_chart(data)
    else:
        chart_url = None
        img = None
        logging.warning(f"No data available for {base_currency} -> {target_currency} on {report_date}")

    # Biggest change in 7-day window
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                base_currency,
                target_currency,
                MAX(rate) AS max_rate,
                MIN(rate) AS min_rate,
                (MAX(rate) - MIN(rate)) / MIN(rate) * 100 AS percentage_change
            FROM 
                conversion_rates
            WHERE 
                base_currency = %s AND target_currency = %s
                AND date BETWEEN %s - INTERVAL 6 DAY AND %s
            GROUP BY 
                base_currency, target_currency
        """, (base_currency, target_currency, report_date, report_date))
        biggest_change = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        logging.error(f"Database query error while fetching biggest change for {base_currency} -> {target_currency}: {e}")
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
    app.run(debug=True)

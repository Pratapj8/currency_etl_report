from flask import Flask, render_template
import mysql.connector
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib

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

# Fetch the last 7 days of conversion rates
def fetch_rolling_7_day_data(base_currency, target_currency):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, rate
        FROM conversion_rates
        WHERE base_currency = %s AND target_currency = %s
        AND date BETWEEN CURDATE() - INTERVAL 6 DAY AND CURDATE()
        ORDER BY date
    """, (base_currency, target_currency))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# Generate a line chart for the conversion rates
def generate_chart(data):
    dates = [item[0] for item in data]
    rates = [item[1] for item in data]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, rates, marker='o', linestyle='-', color='b')
    plt.title("Rolling 7-Day Conversion Rates")
    plt.xlabel("Date")
    plt.ylabel("Conversion Rate")
    plt.xticks(rotation=45)
    
    # Save the plot to a BytesIO object and encode it to base64 for display in HTML
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
    return chart_url

# Home route
@app.route('/')
def index():
    base_currency = 'USD'  # Example base currency
    target_currency = 'EUR'  # Example target currency
    
    # Fetch rolling 7-day data
    data = fetch_rolling_7_day_data(base_currency, target_currency)
    
    # Generate the chart
    chart_url = generate_chart(data)

    # Fetch the biggest gain/loss
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
            AND date BETWEEN CURDATE() - INTERVAL 6 DAY AND CURDATE()
        GROUP BY 
            base_currency, target_currency
    """, (base_currency, target_currency))
    biggest_change = cursor.fetchone()
    cursor.close()
    conn.close()

    # Render the result in HTML
    return render_template('index.html', chart_url=chart_url, biggest_change=biggest_change)

if __name__ == '__main__':
    app.run(debug=True)

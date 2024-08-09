from flask import Flask, render_template, send_from_directory, jsonify
import subprocess
import mysql.connector
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Database connection parameters
db_config = {
    'user': 'admin',
    'password': '374EdtWCLdLrcvrdYTIi',
    'host': 'traffic-db.c7ee2qka2xm0.us-east-2.rds.amazonaws.com',
    'database': 'Apple_stock',
}

def get_latest_date():
    try:
        connection = mysql.connector.connect(**db_config)
        query = "SELECT MAX(Date) AS latest_date FROM stock_data"
        df = pd.read_sql(query, connection)
        connection.close()
        return df['latest_date'].iloc[0]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

@app.route('/')
def index():
    latest_date = get_latest_date()
    if latest_date:
        return render_template('index.html', latest_date=latest_date)
    else:
        return render_template('index.html', latest_date="Error fetching date")

@app.route('/plot.png')
def plot():
    return send_from_directory('static', 'plot.png')

@app.route('/predictions.txt')
def predictions():
    return send_from_directory('static', 'predictions.txt', mimetype='text/plain')

@app.route('/refresh')
def refresh():
    try:
        # Run the scripts using the full path to the Python interpreter in your virtual environment
        subprocess.run(['/home/ubuntu/myenv/bin/python', 'insert_api_data.py'], check=True)
        subprocess.run(['/home/ubuntu/myenv/bin/python', 'model.py'], check=True)
        latest_date = get_latest_date()
        if latest_date:
            return jsonify({'success': True, 'latest_date': latest_date.strftime('%Y-%m-%d')})
        else:
            return jsonify({'success': False, 'message': 'Failed to fetch latest date after refresh.'})
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'message': f'Failed to refresh data. Error: {e}'})

@app.route('/test-tf')
def test_tf():
    try:
        import tensorflow as tf
        return f"TensorFlow version: {tf.__version__}"
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)

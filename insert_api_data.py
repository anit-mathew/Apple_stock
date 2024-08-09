import requests
import pandas as pd
from mysql.connector import Error
from common_db import get_db_connection, create_table, data_exists

# Alpha Vantage API key
api_key = 'KJI7TZJZ0VA6WA5O'
symbol = 'AAPL'
interval = 'daily'  # or 'weekly', 'monthly'

# Fetch data from Alpha Vantage
def fetch_stock_data(api_key, symbol, interval):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': f'TIME_SERIES_{interval.upper()}',
        'symbol': symbol,
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
     
    # Check for errors in the API response
    if 'Error Message' in data:
        raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
    elif 'Information' in data:
        raise ValueError(f"Alpha Vantage API Information: {data['Information']}")
    
    return data

def extract_data(data):
    if 'Time Series (Daily)' in data:
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame(time_series).T
        print(df.columns)  # Print the columns to verify their names
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date', '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. volume': 'Volume'}, inplace=True)
        
        # Convert the 'Date' column to datetime.date
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(int)
        return df
    else:
        raise ValueError("Error fetching data from Alpha Vantage")


# Insert data from API into the database
def insert_api_data(cursor, df):
    for _, row in df.iterrows():
        if not data_exists(cursor, row['Date']):
            insert_query = """
            INSERT INTO stock_data (Date, Open, High, Low, Close, Volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, tuple(row))


# Function to check if table exists
def table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    return result is not None

def main():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        print("Connection secured")
        
        # Check if table exists
        if not table_exists(cursor, 'stock_data'):
            print("Creating table")
            create_table(cursor)
        else:
            print("Table already exists")

        # Fetch and insert data from API
        print("Fetching data from API")
        api_data = fetch_stock_data(api_key, symbol, interval)
        df_api = extract_data(api_data)
        print("Inserting API data")
        insert_api_data(cursor, df_api)

        # Commit the transaction
        connection.commit()
        print("API data insertion completed")

    except Error as e:
        print(f"Database Error: {e}")
    except ValueError as ve:
        print(f"Value Error: {ve}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed")

if __name__ == "__main__":
    main()

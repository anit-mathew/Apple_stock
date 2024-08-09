import pandas as pd
from mysql.connector import Error
from common_db import get_db_connection, create_table, data_exists

# Read data from CSV and insert it into the database if it doesn't already exist
def insert_csv_data(cursor, df):
    for _, row in df.iterrows():
        if not data_exists(cursor, row['Date']):
           
            insert_query = """
            INSERT INTO stock_data (Date, Open, High, Low, Close, Volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            # Ensure tuple has the correct number of elements
            values = (row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'])

            cursor.execute(insert_query, values)

def main():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        print("Connection secured")
        
        # Create table if not exists
        print("Creating table")
        create_table(cursor)

        # Read data from CSV
        csv_file = 'Apple.csv'
        df_csv = pd.read_csv(csv_file)
        
        # Drop 'Adj_Close' column if it exists in the DataFrame
        if 'Adj_Close' in df_csv.columns:
            df_csv = df_csv.drop(columns=['Adj_Close'])
        
        print("Inserting CSV data")
        insert_csv_data(cursor, df_csv)

        # Commit the transaction
        connection.commit()
        print("CSV data insertion completed")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Connection closed")

if __name__ == "__main__":
    main()

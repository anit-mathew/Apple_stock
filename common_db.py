import mysql.connector
from mysql.connector import Error

# Database connection parameters
db_config = {
    'user': 'admin',
    'password': '374EdtWCLdLrcvrdYTIi',
    'host': 'traffic-db.c7ee2qka2xm0.us-east-2.rds.amazonaws.com',
    'database': 'Apple_stock',
}

# Function to create the table if it doesn't exist
def create_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS stock_data (
        Date DATE PRIMARY KEY,
        Open FLOAT,
        High FLOAT,
        Low FLOAT,
        Close FLOAT,
        Volume BIGINT
    )
    """
    print("succefully done")
    cursor.execute(create_table_query)

# Function to check if data already exists
def data_exists(cursor, date):
    check_query = "SELECT COUNT(*) FROM stock_data WHERE Date = %s"
    cursor.execute(check_query, (date,))
    return cursor.fetchone()[0] > 0

def get_db_connection():
    return mysql.connector.connect(**db_config)

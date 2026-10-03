import pymysql

# Database credentials
host = "localhost"
user = "root"
password = "123456"
database = "autowebdb"

try:
    # Connect to MySQL server (no database selected yet)
    connection = pymysql.connect(host=host, user=user, password=password)
    cursor = connection.cursor()
    
    # Create database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print(f"Database '{database}' created or already exists.")
    
    cursor.close()
    connection.close()
except Exception as e:
    print(f"Error creating database: {e}")

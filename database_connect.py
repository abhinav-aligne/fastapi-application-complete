import os
from dotenv import load_dotenv
from functools import lru_cache
import mysql.connector as SQL

#lru_cache use: for retriving environment variables using cache memory
@lru_cache
def load_env_variables():
    return load_dotenv()

# Connect to MySQL database
def connectivity():
    mydb = SQL.connect(
            user = os.getenv("user"),
            password = os.getenv("password"),
            host = os.getenv("host"),         
            port = os.getenv("port") 
    )
    mycursor = mydb.cursor(buffered=True)

    # Check if the database exists
    check_database_query = "SHOW DATABASES LIKE 'banking'"
    mycursor.execute(check_database_query)

    # Fetch the result of the query
    existing_databases = mycursor.fetchall()
    
    # If database doesn't exist, so creeating it
    if not existing_databases:
        create_database_query = "CREATE DATABASE banking"
        mycursor.execute(create_database_query)
    return mydb, mycursor

def table_banking():
    # Use the database banking
    mydb, mycursor = connectivity()
    sql1 = "USE banking"
    mycursor.execute(sql1)
    sql2 = '''
                CREATE TABLE IF NOT EXISTS accounts 
                (
                    name_customer VARCHAR(100) NOT NULL,
                    account_id INT PRIMARY KEY,
                    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
                    pin CHAR(4) NOT NULL
                );
                '''
    mycursor.execute(sql2)
    mydb.commit()

def user_banking():
    mydb, mycursor = connectivity()
    sql1 = "USE banking"
    mycursor.execute(sql1)
    sql2 = '''
                CREATE TABLE IF NOT EXISTS users 
                (
                    username VARCHAR(100) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    created_at VARCHAR(100) NOT NULL
                );
                '''
    mycursor.execute(sql2)
    mydb.commit()
import mysql.connector
from flask import current_app

def get_db_connection():
    """
    Establishes a connection to the MySQL database using credentials 
    stored in the Flask application's configuration (loaded from .env).

    Returns: A MySQL Connection object, or None if the connection fails.
    """
    
    # The Config class in app.py loaded these from the .env file.
    db_host = current_app.config.get('DB_HOST')
    db_user = current_app.config.get('DB_USER')
    db_password = current_app.config.get('DB_PASSWORD')
    db_name = current_app.config.get('DB_NAME')



    # Basic check to ensure credentials are set
    if not all([db_host, db_user, db_password, db_name]):
        print("ERROR: Database connection settings are missing. Please check your .env file and Config class in app.py.")
        return None

    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return connection
    
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None
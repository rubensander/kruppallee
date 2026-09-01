import os
import mysql.connector
import logging

logging.basicConfig(level=logging.WARNING)

def check_invalid_values_in_database():
    db_host = os.environ.get("DB_HOST")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_database = os.environ.get("DB_DATABASE")

    connection = mysql.connector.connect(host=db_host, user=db_user, database=db_database, password=db_password)

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM departures WHERE delay > 60 or delay < -60")  # Adjust the condition based on your definition of invalid values
    invalid_rows = cursor.fetchall()

    if invalid_rows:
        logging.warning(f"Found {len(invalid_rows)} rows with invalid delay values in the database.")
        for row in invalid_rows:
            logging.warning(f"Invalid row: {row}")

    # set realtime to 0 for invalid rows
    cursor.execute("UPDATE departures SET realtime = 0 WHERE delay > 60 or delay < 0")
    connection.commit()

    cursor.close()
    connection.close()

if __name__ == "__main__":
    check_invalid_values_in_database()
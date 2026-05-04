# -*- coding: utf-8 -*-
import requests
import mysql.connector
from datetime import datetime as dt
from time import sleep
import sys
import logging
import os
from dotenv import load_dotenv

load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')

API_URL = "https://ifa.ruhrbahn.de/departure/20009409" #9409

def store_data(datetime, line, platform, realdatetime=None, delay=None, realtime=None, direction=None):
    # Connect to MySQL database
    connection = mysql.connector.connect(host=DB_HOST, user=DB_USER, database=DB_DATABASE, password=DB_PASSWORD)
    cursor = connection.cursor()

    # Query to insert data into the database
    insert_query = """
        REPLACE INTO departures (datetime, line, realdatetime, delay, realtime, direction, platform)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    data_tuple = (datetime, line, realdatetime, delay, realtime, direction, platform)
    result = cursor.execute(insert_query, data_tuple)
    connection.commit()
    cursor.close()
    connection.close()

    logging.info(f"Stored data: {data_tuple}")

def main():
    logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().addHandler(logging.FileHandler("log.txt"))

    response = requests.get(API_URL)

    # Statuscode prüfen
    if response.status_code == 200:
        data = response.json()  # Antwort als JSON lesen
        departure_list = data["data"]["departureList"]

        if not departure_list:
            logging.warning("No departures found in the response.")
            return

        for departure in departure_list:

            datetime = parse_datetime(departure["dateTime"])
            line = departure["servingLine"].get("symbol")
            realdatetime = None
            delay = departure["servingLine"].get("delay")
            realtime = departure["servingLine"].get("realtime")
            direction = departure["servingLine"].get("direction")
            platform = departure.get("platform")

            if "realDateTime" in departure:
                realdatetime = parse_datetime(departure["realDateTime"])
            
            store_data(datetime, line, platform, realdatetime, delay, realtime, direction)
    else:
        logging.error(response.status_code)

def parse_datetime(date_dict):
    keys = ['year', 'month', 'day', 'hour', 'minute']
    datetime_dict = {}
    for key in keys:
        if key in date_dict:
            datetime_dict[key] = int(date_dict[key])
        else:
            datetime_dict[key] = 0
    return dt(**datetime_dict)

def loop():
    while True:
        main()
        sleep(300)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        loop()
    else:
        main()
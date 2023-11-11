import psycopg2
import csv
import datetime


conn = psycopg2.connect(
    database="investo_database",
    user="investo_user",
    password="investo_password",
    host="127.0.0.1",
    port="5432",
)

conn.autocommit = True
cursor = conn.cursor()

sql_create_table = """
    CREATE TABLE IF NOT EXISTS HINDALCO_TABLE (
        datetime timestamp,
        close decimal,
        high decimal,
        low decimal,
        open decimal,
        volume integer,
        instrument varchar(255)
    );
"""
cursor.execute(sql_create_table)

csv_file_path = "/home/aprodev_2011/Other Technologies/Investo_Assignment/HINDALCO_1D.xlsx - HINDALCO.csv"

with open(csv_file_path, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Convert datetime string to datetime object
        row["datetime"] = datetime.datetime.strptime(
            row["datetime"], "%Y-%m-%d %H:%M:%S"
        )

        # Convert string values to appropriate data types
        row["close"] = float(row["close"])
        row["high"] = float(row["high"])
        row["low"] = float(row["low"])
        row["open"] = float(row["open"])
        row["volume"] = int(row["volume"])

        # Insert data into the table
        cursor.execute(
            """
                INSERT INTO HINDALCO_TABLE 
                (datetime, close, high, low, open, volume, instrument) 
                VALUES (%(datetime)s, %(close)s, %(high)s, %(low)s, %(open)s, %(volume)s, %(instrument)s);
            """,
            row,
        )

conn.commit()
cursor.close()
conn.close()

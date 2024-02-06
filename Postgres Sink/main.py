import quixstreams as qx
from quix_function import QuixFunction
import os
import psycopg2
from psycopg2 import sql


# Function to insert data into the database
def insert_data(uid, stream_id, timestamp, data):
    # Connect to your postgres DB
    conn = psycopg2.connect(
        dbname="your_dbname",
        user="your_username",
        password="your_password",
        host="your_host",
        port="your_port"
    )

    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        # Prepare the INSERT statement
        query = sql.SQL("""
            INSERT INTO csv_data_parameter_data (uid, stream_id, "timestamp", "data")
            VALUES (%s, %s, to_timestamp(%s), %s);
        """)

        # Execute the query
        cur.execute(query, (uid, stream_id, timestamp, data))

        # Commit the transaction
        conn.commit()

    # Close the connection
    conn.close()


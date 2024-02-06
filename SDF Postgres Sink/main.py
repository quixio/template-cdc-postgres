from quixstreams import Application
from quixstreams.models.serializers.quix import JSONDeserializer

import os
import psycopg2 as p2
from psycopg2 import sql

DB=os.getenv("PG_DATABASE")
HOST=os.getenv("PG_HOST")
PORT=os.getenv("PG_PORT")
USER=os.getenv("PG_USERNAME")
PWD=os.getenv("PG_PASSWORD")

# Function to insert data into the database
def insert_data(conn, uid, stream_id, nanoseconds_timestamp, data):

    # Convert nanoseconds to seconds
    timestamp_seconds = nanoseconds_timestamp / 1e9

    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        # Prepare the INSERT statement
        query = sql.SQL("""
            INSERT INTO csv_data_parameter_data (uid, stream_id, "timestamp", "data")
            VALUES (%s, %s, to_timestamp(%s), %s);
        """)

        # Execute the query
        cur.execute(query, (uid, stream_id, timestamp_seconds, data))

        # Commit the transaction
        conn.commit()

    # Close the connection
    conn.close()


def get_connection():
    # Connect to your postgres DB
    return p2.connect(
        dbname=DB,
        user=USER,
        password=PWD,
        host=HOST,
        port=PORT
    )

def sink_to_pdb(row, conn):
    insert_data(conn, row["Number"], "data-stream", row["Timestamp"], row["Name"])

    print(row)


def main():


    # Create a closure that takes a row and uses the conn from the outer scope
    def sink_to_pdb_with_conn(row):
        sink_to_pdb(conn, row)

    conn = get_connection()

    app = Application.Quix("transformation-v1", auto_offset_reset="earliest")

    input_topic = app.topic(os.environ["input"], value_deserializer=JSONDeserializer())

    sdf = app.dataframe(input_topic)

    # Here put transformation logic.
    sdf = sdf.update(sink_to_pdb_with_conn, stateful=False)

    #sdf = sdf.update(lambda row: print(row))

    app.run(sdf)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")

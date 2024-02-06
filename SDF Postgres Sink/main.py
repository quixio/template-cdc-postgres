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


print(DB)
print(HOST)
print(PORT)
print(USER)
print(PWD)


def get_connection():
    # Connect to your postgres DB
    return p2.connect(
        dbname=DB,
        user=USER,
        password=PWD,
        host=HOST,
        port=PORT
    )

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



def sink_to_pdb(conn, row):
    insert_data(conn, row["Number"], "data-stream", row["Timestamp"], row["Name"])

    print(row)


def main():


    # Create a closure that takes a row and uses the conn from the outer scope
    def sink_to_pdb_with_conn(row):
        try:
            sink_to_pdb(conn, row)
        except Exception as e:
            print(f"An error occurred: {e}")

    conn = get_connection()

    app = Application.Quix("transformation-v1", auto_offset_reset="earliest")

    input_topic = app.topic(os.environ["input"], value_deserializer=JSONDeserializer())

    sdf = app.dataframe(input_topic)

    sdf = sdf.update(sink_to_pdb_with_conn)

    app.run(sdf)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        
        print("Exiting.")

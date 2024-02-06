from quixstreams import Application, State
from quixstreams.models.serializers.quix import JsonDeserializer

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


def sink_to_pdb(row):
    print(row)


def main():
    app = Application.Quix("transformation-v1", auto_offset_reset="latest")

    input_topic = app.topic(os.environ["input"], value_deserializer=JsonDeserializer())

    sdf = app.dataframe(input_topic)

    # Here put transformation logic.
    sdf = sdf.update(sink_to_pdb)

    #sdf = sdf.update(lambda row: print(row))

    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")

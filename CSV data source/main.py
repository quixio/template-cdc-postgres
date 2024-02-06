# Import the Quix Streams modules for interacting with Kafka:
from quixstreams import Application
from quixstreams.models.serializers.quix import SerializationContext, JSONSerializer

# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# Import additional modules as needed
import pandas as pd
import random
import time
import os

app = Application.Quix(consumer_group="csv_sample", auto_create_topics=True)  # Create an Application
serializer = JSONSerializer()  # Define a serializer for messages, using JSON Serializer for ease

topic_name = os.environ["output"]  # Define the topic using the "output" environment variable
topic = app.topic(topic_name)

script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the current script
csv_file_path = os.path.join(script_dir, "demo-data.csv")  # Construct the path to the CSV file

# this function loads the file and sends each row to the publisher
def read_csv_file(file_path: str):
    """
    A function to read data from a CSV file in an endless manner.
    It returns a generator with stream_id and rows
    """

    print("CSV file loading.")
    df = pd.read_csv(file_path)  # Read the CSV file into a pandas.DataFrame
    print("File loaded.")

    row_count = len(df)  # Get the number of rows in the dataFrame for printing out later

    stream_id = f"CSV_DATA_{str(random.randint(1, 100)).zfill(3)}"# Generate a unique ID for this data stream.  # It will be used as a message key in Kafka.

    headers = df.columns.tolist()# Get the column headers as a list

    while True:  # Continuously loop over the data
        print(f"Publishing {row_count} rows.")

        for _, row in df.iterrows():
            row_data = {header: row[header] for header in headers}
            row_data["Timestamp"] = time.time_ns()
            yield stream_id, row_data

        print("All rows published")

        time.sleep(1)


def main():
    """
    Read data from the CSV file and publish it to Kafka
    """

    # Create a pre-configured Producer object.
    # Producer is already setup to use Quix brokers.
    # It will also ensure that the topics exist before producing to them if
    # Application.Quix is initiliazed with "auto_create_topics=True".
    producer = app.get_producer()

    with producer:
        # Iterate over the data from CSV file
        for message_key, row_data in read_csv_file(file_path=csv_file_path):
            # Serialize row value to bytes
            serialized_value = serializer(value=row_data, ctx=SerializationContext(topic=topic.name))

            # publish the data to the topic
            producer.produce(topic=topic.name, key=message_key, value=serialized_value,)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")
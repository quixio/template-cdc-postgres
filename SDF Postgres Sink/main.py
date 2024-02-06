import os
from quixstreams import Application
from quixstreams.models.serializers.quix import QuixDeserializer


app = Application.Quix("transformation-v1", auto_offset_reset="latest")

input_topic = app.topic(os.environ["input"], value_deserializer=QuixDeserializer())

sdf = app.dataframe(input_topic)

# Here put transformation logic.

sdf = sdf.update(lambda row: print(row))

if __name__ == "__main__":
    app.run(sdf)
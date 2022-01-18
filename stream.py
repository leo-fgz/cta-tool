from client import Client
from config import STREAM_COLLECTION, ACADEMIC_TOKEN


client=Client(ACADEMIC_TOKEN)

# delete existing rules
client.delete_all_rules()

# set new rules
client.set_rules()

# run stream in loop in case of disconnect
while True:
    for response in client.stream():
        if "errors" in response:
            continue
        client.add_to_database(STREAM_COLLECTION,[response])



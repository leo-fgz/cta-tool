from pymongo import MongoClient
import subprocess
from config import CONVERSATIONS_COLLECTION, STREAM_COLLECTION, DB_ADDRESS, MONGO_DB_NAME


# setup Database
db_client = MongoClient(DB_ADDRESS)
db = db_client[MONGO_DB_NAME]
stream_col = db[STREAM_COLLECTION]
conversations_col = db[CONVERSATIONS_COLLECTION]

# get existing tweets
streamed_tweets = stream_col.find()
conversation_tweets = conversations_col.find()

conv_ids = [i["data"]["conversation_id"] for i in streamed_tweets]

# check if conversations collection is empty
if conversation_tweets is None:
    existing_conv_ids = []
else:
    existing_conv_ids = [i["data"]["conversation_id"] for i in conversation_tweets]

# subtract existing conversation ids in database from new conversations
conv_ids_to_query = set(conv_ids) - set(existing_conv_ids)

# search for tweets and store in database
for conv_id in conv_ids_to_query:
    tweet=stream_col.find_one({"data.conversation_id":conv_id})
    if "conversation_tweet_count" in tweet:
        continue
    subprocess.call(["./sub_conversation.py",conv_id])

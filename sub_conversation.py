#!/home/tuser/kn-twitter/venv/bin/python
# set shebang according to server environment

import sys
from client import Client
from pymongo import MongoClient
from uuid import uuid4
from dateutil.parser import parse
from datetime import datetime, timedelta
from config import ACADEMIC_TOKEN, REQUESTED_FIELDS, CONVERSATIONS_COLLECTION, STREAM_COLLECTION, DB_ADDRESS, \
    MONGO_DB_NAME

client = Client(ACADEMIC_TOKEN)

# get conversation-id from main process
conv_id = sys.argv[1]

# setup Database
db_client = MongoClient(DB_ADDRESS)
db = db_client[MONGO_DB_NAME]
stream_col = db[STREAM_COLLECTION]
conversations_col = db[CONVERSATIONS_COLLECTION]

# check if tweet younger than 7 days and ignore those
db_query = {"data.conversation_id": conv_id}
tweet = stream_col.find_one(db_query)
original_tweet_id = tweet["data"]["id"]
if "referenced_tweets" in tweet["data"]:
    original_referenced_id = tweet["data"]["referenced_tweets"][0]["id"]
else:
    original_referenced_id = "0"

today = datetime.now()
tweet_date = parse(tweet["data"]["created_at"][:-1])
last_week = timedelta(days=7)
if last_week > today - tweet_date:
    print(tweet_date, "tweet  younger than 7 days")
    exit()
print(tweet_date, "https://twitter.com/anyuser/status/" + conv_id)

# set original_follower_count
conversation_tweet = client.get_single_tweet(conv_id, REQUESTED_FIELDS)
follower_count = conversation_tweet["includes"]["users"][0]["public_metrics"]["followers_count"]
new_values = {"$set": {"original_follower_count": follower_count}}
stream_col.update_many(db_query, new_values)

# check if response is empty ->conversation metrics=0
params = REQUESTED_FIELDS
params["query"] = "conversation_id:" + conv_id
response = client.search_tweet(params, "full")
if len(response) == 0:
    new_values = {"$set": {"conversation_tweet_count": "0",
                           "conversation_user_count": "0"}}
    stream_col.update_many(db_query, new_values)
    print("empty conversation response")
    exit()

# add root conversation-tweet to response, get updated tweet metrics and update stream data metrics
if "public_metrics" in conversation_tweet["data"]:
    response.append(conversation_tweet)
    retweet_count = conversation_tweet["data"]["public_metrics"]["retweet_count"]
    reply_count = conversation_tweet["data"]["public_metrics"]["reply_count"]
    like_count = conversation_tweet["data"]["public_metrics"]["like_count"]
    quote_count = conversation_tweet["data"]["public_metrics"]["quote_count"]
    new_values = {"$set": {"data.public_metrics.retweet_count": retweet_count,
                           "data.public_metrics.reply_count": reply_count,
                           "data.public_metrics.like_count": like_count,
                           "data.public_metrics.quote_count": quote_count}}
    stream_col.update_many(db_query,new_values)

# add matching rule tag to conversation response and add to database
for r in response:
    r["matching_rules"] = [{"tag": tweet["matching_rules"][0]["tag"]}]
    conversations_col.insert_one(r)

# update conversation metrics
conversation_tweet_count = conversations_col.count_documents(db_query)
conversation_user_count = len(conversations_col.find(db_query).distinct("data.author_id"))
new_values = {"$set": {"conversation_tweet_count": str(conversation_tweet_count),
                       "conversation_user_count": str(conversation_user_count),
                       "has_response":has_response}}
stream_col.update_many(db_query, new_values)
print(conversation_user_count, conversation_tweet_count)

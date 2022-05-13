from uuid import uuid4
from pymongo import MongoClient
from config import CONVERSATIONS_COLLECTION, STREAM_COLLECTION, DB_ADDRESS, MONGO_DB_NAME

db_client = MongoClient(DB_ADDRESS)
db = db_client[MONGO_DB_NAME]
stream_col = db["STREAM_COLLECTION"]
conversations_col = db["CONVERSATIONS_COLLECTION"]

stream_collection = stream_col.find({"matching_rules.tag": "MY_MATCHING_RULES_TAG"})
counter = 0
for index_tweet in stream_collection:
    counter += 1
    print(counter)
    
    #get index tweet
    index_tweet_id = index_tweet["data"]["id"]
    conversation = conversations_col.find({"data.conversation_id": conversation_id})


    sub_conversation_id = uuid4()
    new_values = {"$set": {"sub_conversation_id": sub_conversation_id}}
    tweet_ids = [index_tweet_id]

    # setting check variable to set index tweet subconversation id
    index_tweet_has_subconversation = False

    # getting replies
    for tweet_id in tweet_ids:
        following_tweets=conversations_col.find({"data.referenced_tweets.id":tweet_id})

        # loop through replies in case there are replies and set sub_conv_id
        for following_tweet in following_tweets:
            tweet_ids.append(following_tweet["data"]["id"])
            conversations_col.update_one({"_id": following_tweet["_id"]}, new_values)
            index_tweet_has_subconversation=True
            print("index has reply")

    # getting past conversations
    if "referenced_tweets" in index_tweet["data"] and conversation_id != index_tweet_id:
        referenced_ids = []

        # in case there are multiple referenced tweets add them to list
        for referenced_id in index_tweet["data"]["referenced_tweets"]:
            referenced_ids.append(referenced_id["id"])
        
        # loop through referenced ids in case there are multiple referenced tweets in index tweet
        for referenced_id in referenced_ids:
            referenced_tweets=conversations_col.find({"data.id":referenced_id})
            
            # loop through referenced tweets of referenced tweets and set sub_conv_id
            for referenced_tweet in referenced_tweets:
                conversations_col.update_one({"_id":referenced_tweet["_id"]},new_values)
                index_tweet_has_subconversation=True
                print("index has previous conversation")
                if "referenced_tweets" in referenced_tweet["data"]:
                    for r_id in referenced_tweet["data"]["referenced_tweets"]:
                        referenced_ids.append(r_id["id"])

    # if index tweet has subconversation -> set id
    if index_tweet_has_subconversation:
        conversations_col.update_one({"data.id":index_tweet_id},new_values)

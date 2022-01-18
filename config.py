# Twitter credentials
ACADEMIC_TOKEN = "YOUR_TOKEN"
PRIVATE_TOKEN = "YOUR_TOKEN"

# MongoDB Database and collection names
MONGO_DB_NAME = "twitter"
STREAM_COLLECTION = "stream"
CONVERSATIONS_COLLECTION = "conversations"


# Database address
DB_ADDRESS = "mongodb://localhost:27017"

# Requested twitter-data
REQUESTED_FIELDS = {"tweet.fields": 'author_id,conversation_id,created_at,id,public_metrics,text',
                    "expansions": 'author_id,referenced_tweets.id,in_reply_to_user_id',
                    "media.fields": "type,preview_image_url,url",
                    "user.fields": 'created_at,name,public_metrics,url,username'}

# Stream filter rules in a list of dicts
FILTER_RULES = [{"value": '"enter your filter rules" -is:retweet', "tag": "filtertag"}]

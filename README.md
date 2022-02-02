# Conversation-focused Tweet Analysis

This tool collects tweets and conversations by using Twitter's API V2 filtered stream and search endpoint, and it calculates a series of conversational metrics for conversation-based sampling and filtering to assist qualitative research. The tool has been tested using Twitter's academic API but it was developed to be easily adopted by researchers using Twitter's non-academic product track.

# Long Description

The aim of the CTA tool is to assist researcher in the identification and filtering of tweets based on their conversational context. To do so, it employs a series of quantitative indicators, some of which are provided by Twitter directly while others must be calculated after tweets have been captured. Currently, the tool retrieves or generates the following indicators: 

- the follower count of the original account who started the conversation (origin follower count / OFC, provided by Twitter directly),
- the conversation user count (CUC), 
- the conversation tweet count (CTC),
- whether or not a tweet has a response.

The main goal for the development of the tool is the subsequent qualitative analysis of the content of tweets and of the conversational dynamics in which they are embedded. The above-mentioned indicators can be used to sort or filter captured tweets according to conversational indicators and thereby reduce the sample size for qualitative analysis.

# Scripts

The config.py defines essential variables for retrieving data from Twitter (developer credentials, requested fields, filter rules for the filtered stream endpoint) and where the retrieved data should be stored. 

The client.py defines the functions and parameters that exercise communication with the different endpoints of the Twitter API and with the local database. It includes sleep functions for each retrieval subprocess to mitigate failures based on connection issues or Twitter's rate limit.

The stream.py runs the script for retrieving tweets ("index tweets") from the filtered stream endpoint of the Twitter API and stores them in the "stream_collection" of the local database.

The get_conversation.py identifies for which tweets in the stream_collection a conversation has not yet been retrieved. Matching results are then handled by the sub_conversation.py. The script uses the search endpoint of the Twitter API and retrieves the entire conversation of each index tweet in the stream_collection after 7 days have passed and stores them in the "conversations_collection" of the local database.

The sub_conversation.py also calculates or retrieves the quantitative conversational indicators mentioned above (OFC, CUC, CTC, has response) and adds these values to the stream_collection of the local database. To later identify the tweets that not only share the same conversation ID but are part of the same sub-conversation or reply chain, the sub_conversation.py appends additional tags to all tweets of a sub-conversation and stores them in the conversation_collection.

# Database

Data is stored and accessed in two separate collections using mongo.db. The "stream_collection" of the local database keeps the index tweets and their metadata fields, their respective OFC, CUC, and CTC values, and additional entry fields for manual annotation. The "conversations_collection" holds all the conversation tweets and additional tags.

# In development

- sub-conversation user count, sub-conversation tweet count
- a 'delete script' is developed to achieve data minimization: after the conversation metrics have been calculated, it deletes irrelevant tweets that are not part of the sub-conversation or reply chain in which the index tweet originally appeared.

# Resources/ Dependencies

- pymongo
- python-dateutil
- requests

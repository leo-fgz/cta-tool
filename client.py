import requests
import json
import time
import datetime
from pymongo import MongoClient
from config import REQUESTED_FIELDS, DB_ADDRESS, FILTER_RULES, MONGO_DB_NAME


class Client:

    def __init__(self,bearer_token):
        self.bearer_token=bearer_token

    def create_headers(self):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def stream(self):
        url = "https://api.twitter.com/2/tweets/search/stream"
        params = REQUESTED_FIELDS
        try:
            with requests.get(url, headers=self.create_headers(), stream=True, params=params) as response:
                print(response.status_code)
                if response.status_code != 200:
                    raise Exception(
                        "Cannot get stream (HTTP {}): {}".format(
                            response.status_code, response.text
                        )
                    )
                for response_line in response.iter_lines():
                    if response_line:
                        json_response = json.loads(response_line)
                        print(json.dumps(json_response, indent=4, sort_keys=True))
                        yield json_response

        # in case of an exception, wait 10s and reconnect after that
        except Exception as e:
            print(e)
            time.sleep(10)
            pass

    def set_rules(self):

        # adds rules
        url = "https://api.twitter.com/2/tweets/search/stream/rules"
        rules = FILTER_RULES
        params = {"add": rules}
        response = requests.post(
            url,
            headers=self.create_headers(),
            json=params,
        )
        if response.status_code != 201:
            raise Exception(
                "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        print(json.dumps(response.json()))

    def get_rules(self):
        url = "https://api.twitter.com/2/tweets/search/stream/rules"
        response = requests.get(
            url,
            headers=self.create_headers()
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        print(json.dumps(response.json()))
        return response.json()

    def delete_all_rules(self):
        url = "https://api.twitter.com/2/tweets/search/stream/rules"
        rules = self.get_rules()
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        params = {"delete": {"ids": ids}}
        response = requests.post(
            url,
            headers=self.create_headers(),
            json=params
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot delete rules (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        print(json.dumps(response.json()))

    def add_to_database(self, collection, data):
        client = MongoClient(DB_ADDRESS)
        db = client[MONGO_DB_NAME]
        collection = db[collection]
        collection.insert_many(data)

    def search_tweet(self, params, search_type):
        search_url=""
        if search_type == "full":
            search_url = "https://api.twitter.com/2/tweets/search/all"
            start_time=str(datetime.datetime(2021,1,1).replace(microsecond=0).isoformat())+"Z"
            params["start_time"]=start_time
            params["max_results"] = 500
        if search_type == "standard":
            search_url = "https://api.twitter.com/2/tweets/search/recent"
            params["max_results"] = 100
        tweets = []
        next_token = 0
        while next_token != 1:
            # twitter request limit 1s per request
            time.sleep(1.1)

            if next_token != 0:
                params["next_token"] = next_token
            response = requests.request("GET", search_url, headers=self.create_headers(), params=params)

            if response.status_code != 200:
                raise Exception(response.status_code, response.text)

            if int(response.headers["x-rate-limit-remaining"]) == 1:
                time.sleep(int(response.headers["x-rate-limit-reset"])-int(time.time())+5)
            response = response.json()

            if int(response["meta"]["result_count"]) == 0:
                print(response)
                break

            if "next_token" in response["meta"]:
                next_token = response["meta"]["next_token"]
            else:
                next_token = 1

            tweets += self.merge_full_search(response)

        return tweets

    def merge_full_search(self, r):
        tweets = []
        for item in r["data"]:
            dic={}
            dic["data"] = item
            for user in r["includes"]["users"]:
                if int(user["id"]) == int(item["author_id"]):
                    dic["includes"]={}
                    dic["includes"]["users"]=[user]
                    break
            tweets.append(dic)
        return tweets

    def get_single_tweet(self, tweet_id, additional_params):
        search_url = "https://api.twitter.com/2/tweets/" + str(tweet_id)
        response = requests.request("GET", search_url, headers=self.create_headers(), params=additional_params)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        if int(response.headers["x-rate-limit-remaining"]) == 0:
            time.sleep(960)
        # twitter rate limit
        time.sleep(1.1)
        return response.json()

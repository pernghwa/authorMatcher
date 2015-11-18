import tweepy
from elasticsearch import Elasticsearch
#TWITTER API

USER_KEY = "rX0n8E8AsfbXkOQXyWIZIGDYq"
USER_SECRET = "vuxpSPVy5xDLaM3fkCqs1fK10Ldaw1LumywNPYdzDLkf9oasfC"
USER_TOKEN = "500420636-kZHWR2CJAYAGKGuXNyrBKKDRtEXFqio0rJDSZ6Xj"
USER_TOKEN_SECRET = "BojXlL7UKaMAyvcyO87tsjTnEG7OppphvZVMXmcbpBDph"
CONSUMER_KEY = "P6F9glaUd7uB3kj5ElRWRXIDm"
CONSUMER_SECRET = "lasmKKLlE0WzOXTe61u1s1PERsuKludoUIkY9W2XWkHf6xxbsW"
ACCESS_TOKEN = "2832004285-wvzniXfCRDi3YyiXa8fTxPcHUNscIAWj5TtNtPo"
ACCESS_TOKEN_SECRET = "6lcArRNPYPxruE0BGCpqlHwLSq3DN4QCw9F1fluT1uO68"

# user context twitter api is needed to get information like user search:
# https://dev.twitter.com/oauth/application-only
user_auth = tweepy.OAuthHandler(USER_KEY, USER_SECRET)
user_auth.set_access_token(USER_TOKEN, USER_TOKEN_SECRET)
twitter_api = tweepy.API(user_auth)

#GNIP API

GNIP_USERNAME="username"
GNIP_PASSWORD="password"

#ES database
DB_INDEX = "twitter_journalist"
es = Elasticsearch()

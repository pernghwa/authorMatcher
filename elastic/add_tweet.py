# utilities for adding tweet JSON objects to elasticsearch instance
import time, datetime
from config import *
from esUtil import *

DEFAULT_DATE = datetime.datetime.strptime("Jan 30 2015 12:00PM", '%b %d %Y %I:%M%p')

def add_tweet_es(tweet_json,es):
    tid = tweet_json['id']
    del(tweet_json['id'])
    es.add(index=DB_INDEX,doc_type='tweet',id=tid,body=tweet_json)

# crawl all tweets in user timeline after cdate
def add_timeline_es(user,es,cdate=DEFAULT_DATE,timeout=5,verbose=False):
    for u,tweet in add_timeline(user,es,cdate,timeout,verbose)
        t = add_tweet_es(tweet2json(tweet._json,user['id']),es)

if __name__ == "__main__":
    users = [{'tweep_id':int(l.split(',')[1].strip())} for l in file('../data/test_users.txt','r').readlines()]
    add_timeline_es(users[0],es,verbose=True)

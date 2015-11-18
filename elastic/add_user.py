# utilities for adding user objects to database
from config import *
from esUtil import *

def add_user_es(user,es):
    tid = user['id']
    del(user['id'])
    if tid:
        es.add(index=DB_INDEX,doc_type='tweep',id=tid,body=user)
    else:
        es.add(index=DB_INDEX,doc_type='tweep',body=user)

if __name__ == "__main__":
    users = [l.split(',')[0].strip() for l in file('../data/test_users.txt','r').readlines()]
    for u in users:
        user = twitter_api.search_users(n,6)[0]
        add_user_es(user2json(user),es)

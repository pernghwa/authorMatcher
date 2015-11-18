from elasticsearch import ElasticSearch
from config import *

def user2json(u,query={'id':None,'news_organization':None}):
    return {'id':query['id'],
            'fullname':query['fullname']
            'tweep_id':u.id,
            'news_organization':query['org'],
            'screen_name':u.screen_name,
            'description':u.description.encode('utf8').replace('\n','').replace('\r',''),
            'created_at':u.created_at,
            'statuses_count':u.statuses_count,
            'followers_count':u.followers_count,
            'favourites_count':u.favourites_count,
            'following':[]}

def tweet2json(t,uid=None):
    out = t
    out['tweep_id'] = out['user']['id']
    del(out['user'])
    # set entity id if u is available
    if uid:
        out['ent_id'] = uid
    return out

def loadES(cat,fun):
    data = es.search(index=DB_INDEX,doc_type=cat,body={"query":{"match_all":{}}})['hits']['hits']
    return filter(fun,data)

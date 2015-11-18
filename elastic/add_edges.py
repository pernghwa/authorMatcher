# utilities for adding following relations to query user set
from collections import defaultdict
from elasticsearch import helpers
from config import *
from esUtil import *

def add_neighbors_es(inSet,es):
    data = defaultdict(list)
    tid2id = [n['_source']['tweep_id']:n['_id'] for n in es.search(index=DB_INDEX,
    doc_type="tweep",body={"query": {"match_all": {}}})['hits']['hits'] if 'tweep_id' in n['_source']]

    def add_data(data):
        actions = []
        nodemap = es.mget(index=DB_INDEX,doc_type="tweep",body={'ids':[str(tid2id[str(d)]) for d in data]})['docs']
        nodemap = {d["_id"]:d["_source"] for d in nodemap}
        for d in data:
            action = {
                "_index":DB_INDEX,
                "_type":"tweep",
                "_id":tid2id[d],
                "_source":nodemap[tid2id[d]]
            }
            action['_source']['following'] = data[d]
            actions.append(action)
        helpers.bulk(es,actions)

    count = [0,0]
    for link in add_neighbors(inSet):
        data[link[0]] += [link[1]]
        if count[1] != link[2]:
            count[1] = link[2]
            if count[1] - count[0] > 1500:
                add_data(data)
                data = defaultdict(list)
                count[0] = count[1]
    if len(data) > 0:
        add_data(data)

if __name__ == "__main__":
    users = [int(l.split(',')[1].strip()) for l in file('../data/test_users.txt','r').readlines()]
    add_neighbors_es(users,es)

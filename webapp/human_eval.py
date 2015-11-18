import datetime, pickle, os
from operator import itemgetter
from flask import request, render_template, jsonify, Response, json
from webapp import app, twitter_user_api
from util.featureUtil import
from elastic.esUtil import *

@app.route('/twval/')
def twvalidate():
    return render_template("human_eval.html")

# initialize data
autMap = {}
userGenerator = loadES('author',lambda d:'screen_name' not in d)

try:
    load_data = pickle.load(open(os.getcwd()+'/static/data/outerCircle.pickle','rb'))
    graph_cands = pickle.loads(load_data)
except Exception:
    graph_cands = {}

@app.route('/fresh_id/', methods = ['POST'])
def fresh_id():
    def check_name():
        c = userGenerator.pop()
        if c == None:
            return None, None
        cs = [chosen['fullname']]
        name = remove_middle(cs[0])
        if name != cs[0]:
            cs.append(name)
        return cs, c

    chosen_names, chosen = check_name()
    if not chosen:
        return jsonify(uid=-1,name="",info="",possibles=[])

    while chosen_names[-1] in autMap:
    	chosen_names, chosen = check_name()
        if not chosen:
            return jsonify(uid=-1,name="",info="",possibles=[])

    print len(userGenerator), chosen['fullname'], chosen_names

    possibles = []
    for chosen_name in chosen_names:
	    #search twitter api for the user by name, get top 20 results
    	users = twitter_api.search_users(chosen_name,20)

    	possibles.extend([[x.screen_name,
                  x.name,
                  x.description,
                  x.profile_image_url.replace("normal","400x400"),
                  x.followers_count,
                  x.statuses_count,
                  x.friends_count,
                  x.id in graph_cands]
                 for x in users])

    autMap[chosen['fullname']] = 0
    return jsonify(uid=chosen['ent_id'],name=chosen['fullname'],info=chosen['org'],possibles=possibles)

@app.route('/submit_validation/', methods=["POST"])
def submit_validation():
	print "valid handles"
	valid_handles = [x for x in request.form.getlist('valid_handles[]')]
	print "valid uid"
	uid = int(request.form['uid'])
    # assumes we are searching from elasticsearch for unlabeled authors
    # if the authors are not yet ingested to database, do it first!
	aut = #es.get(index=DB_INDEX,doc_type="tweep",body={"query": {"match_all": {}}})

	for sn in valid_handles:
		u = twitter_api.lookup_users(screen_names=[sn])[0]
		userobj = user2json(u,{})
        es.index()

	return jsonify(uid=uid)

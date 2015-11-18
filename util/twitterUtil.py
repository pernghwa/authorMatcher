import tweepy
from config import twitter_api

def add_neighbors(users):
    '''
    A generator for attaining neighbors for input user set
    Input:
       - users: a list of user ids
    Output:
       - [following_id,followed_id]
    '''
	count = 0
	for ind, user in enumerate(users):
		if ind < 0:
			continue

		if ind % 100 == 0:
			print ind, " users"

		idx = []

		try:
			for page in tweepy.Cursor(twitter_api.friends_ids, user_id=user, wait_on_rate_limit=True).pages():
				idx.extend(page)
		except Exception as e:
			print e
			pass

		for i in idx:
			count += 1
			if count % 100000 == 0:
				print count
			yield [user, i, ind]

# crawl all tweets in user timeline after cdate
def add_timeline(user,es,cdate=DEFAULT_DATE,timeout=5,verbose=False):
    them = twitter_api.lookup_users(user_ids=[user['tweep_id']])[0]

    if them.protected:
        return

    timeline = []
    # backward: find oldest tweet, get all older tweets until the timestamp passes cdate.
    new_tw = twitter_api.user_timeline(id=user['tweep_id'], include_rts=True, count=200)
    if not len(new_tw) == 0:
        oldest_id = new_tw[-1].id
        oldest_time = new_tw[-1].created_at
    time.sleep(timeout)

    while len(new_tw)>0:
        timeline.extend([t for t in new_tw if t.created_at > cdate])
        if oldest_time < cdate:
            break
        oldest_id = new_tw[-1].id
        oldest_time = new_tw[-1].created_at
        new_tw = twitter_api.user_timeline(id=user['tweep_id'], include_rts=True, count=200, max_id=oldest_id)[1:]
        time.sleep(timeout)

    if verbose:
        print "Adding",len(timeline),"potential tweets"

    for idx, tweet in enumerate(timeline):
        yield user,tweet

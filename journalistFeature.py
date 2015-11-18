import string, re
from featureUtil import *
'''
build a classification for politicians with models
 for each name, check top 3 returned accounts
 features
 1. #followers, #tweets, #following, #favorites
 1.5. normalized #followers
 2. relative followers to top 10
 3. top 1 not matched name but top 2 is
 4. matched name
 5. matched last name in display or screen_name
 6. matched full name in display or screen_name
 7. matched 'Rep', 'Sen' in display or screen_name
 8. parody accounts description
 9. interjection
 10. length of description
 11. relative join date
 12. connected with currently matched users
 13. previously labeled user name
 14. edit distance (or hamming distance) of user name
 15. description
 trained on linear kernel SVM
'''

def listmap_author(ref_tw, tweeps):
    # map a list of tweep objects into features
    # pass 1: create relative features
    tmpfea = [[0,0] for i in range(2)]
    tmp = normalize_name(ref_tw)
    name = [n.lower() for n in tmp]
    for tw in tweeps:
        if not tmpfea[0]:
            tmpfea[0] = [tw.followers_count,tw.followers_count]
        else:
            tmpfea[0][0] += tw.followers_count
            tmpfea[0][1] = max(tw.followers_count, tmpfea[0][1])
    tmpfea[0][0] = tmpfea[0][0]/(float(len(tweeps))+1)
    # pass 2: generating features
    cur_match = False
    for idx, tw in enumerate(tweeps):
        feature = []
        twname = tw.name.lower()
        # fea 1: #followers, #following, #tweets, log_normalized #followers
        feature = feature + [tw.followers_count,tw.friends_count,tw.statuses_count,log_normalize(tw.followers_count)]
        # fea 2: relative followers (mean, max)
        feature = feature + [tw.followers_count/(float(tmpfea[0][0])+1), (float(tmpfea[0][1])+1)/(tw.followers_count+1)]
        # fea 4-7: matched name, lastname, fullname, news orgs
        #print twname, name
        if name:
            ln = name[-1]
        else:
            ln = ''
        feature = feature + [iterlist_match((twname+' '+tw.screen_name.lower()).split(),name),
                             iterlist_match((twname+' '+tw.screen_name.lower()).split(),[ln]),
                             iterlist_match(twname.split(), name),
                             list_match(twname+' '+tw.screen_name.lower(),['cnn','nyt','wsj','buzz','bf','npr','fox','politico','post','propublica','reuters'])]
        # fea 3: before top k not matched name but kth is
        if cur_match:
            feature = feature + [0]
        elif feature[9]:
            feature = feature + [1]
            cur_match = True
        else:
            feature = feature + [0]
        # fea 8: news orgs
        feature = feature + [list_match(tw.screen_name.lower()+' '+tw.description.lower(), news_terms+journalist_terms)]
        # fea 9: interjection + abbrev
        feature = feature + [list_match(tw.description.lower(), informal_list)]
        # fea 10: description length
        feature = feature + [len(tw.description)]
        # fea 11: relative join date
        feature = feature + [date_normalize(tw.created_at)]
        # fea 14: edit distance
        feature = feature + [ed_normalize(ref_tw,twname),ed_normalize(ref_tw,tw.screen_name.lower())]
        # fea 15: return length
        feature = feature + [len(tweeps)]
        # fea 16: connected by current set
        feature = feature + [ref_accounts[tw.id] if tw.id in ref_accounts else 0]
        # fea 15: description
        #feature = np.concatanate(np.array(feature),vectorizer.transform(preprocess(tw.description)),axis=0)
        twsn = tw.screen_name
        yield (tw.id, map_feature(feature), ' '.join([regex.sub('', w) for w in tw.description.split()]))

def prepare_accounts(core_accounts,peri_accounts):
    inSet = []
    edgeDict = {}
    ref_accounts = {}

    # first pass: core_accounts
    for p in core_accounts:
        inSet.append(p)

    for cand in add_neighbors(users=inSet):
        edgeDict[(cand[0],cand[1])] = 0
        ref_accounts[cand[1]] = 1

    # second pass: peri_accounts
    count = 0
    for r in ref_accounts:
        count += 1
        if count % 500 == 0:
            print count
        try:
            u = twitter_api.lookup_users(user_ids=[r])[0]
        except Exception:
            print "no user id ", r
        if is_journalist(u.description):
            inSet.append(r)
    for r in peri_accounts:
        inSet.append(r)

    for cand in add_neighbors(users=inSet):
        edgeDict[(cand[0],cand[1])] = 0
        if cand[1] not in ref_accounts:
            ref_accounts[cand[1]] = 0.3

    return ref_accounts

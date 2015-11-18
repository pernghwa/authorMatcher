import re, string, time
import cPickle as pickle

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.svm import LinearSVC
from sklearn.preprocessing import normalize
from sklearn.externals import joblib

from elastic.esUtil import user2json
from journalistFeature import *

class authorMatcher:

    publishing = ['nytimes','npr','washingtonpost','foxnews','cnn','wsj','buzzfeed','politico','propublica','reuters','mcclatchy','latimes','bostonglobe']

    '''
    class authorMatcher:
        uses supervised machine learning model (default: Support Vector Machine)
        to match journalist name to corresponding twitter handle
    initialization + used parameters:
        - soft: uses probability estimates SVM (Pratt)
        - ref_accounts: dict struct storing core+peripheral accounts to news org
        -
    '''
    def __init__(self,soft=False):
        self.soft = soft
        self.thres = 0.5
        self.ref_accounts = None
        self.features = [[],[]]
        self.train_labels = []
        self.vectorizer = CountVectorizer(dtype=float)

    # use joblib for numpy model serialization
    # file name only need to specify directory path
    def load_model(self,fname):
        self.model = joblib.load(fname+'model.pkl')
        self.normalizer = joblib.load(fname+'normalizer.pkl')
        self.vectorizer = joblib.load(fname+'vectorizer.pkl')

    def save_model(self,fname):
        joblib.dump(self.model,fname+'model.pkl')
        joblib.dump(self.normalizer,fname+'normalizer.pkl')
        joblib.dump(self.vectorizer,fname+'vectorizer.pkl')

    # use pickle serialization
    def load_features(self,fname):
        with open(fname,'rb') as infile:
            self.features = pickle.load(infile)

    def save_features(self,fname):
        with open(fname,'wb') as outfile:
            pickle.dump(self.features,outfile)

    def prepare_features(self,core_accounts,peri_accounts,candidates=None):
        '''
        WARNING: INVOKES TWITTER RESTFUL API MULTIPLE TIMES- SLOW EXECUTION!
        call twitter api to get relevant user features for classification
        input:
            core_accounts- publishing accounts from news org
            peri_accounts- peripheral accounts with channels and directly
                           connected accounts to publishing accounts
            candidates- ground truth accounts: {<candidate_name/candidate_id>:{'screen_name':<screen_name>}}
        '''
        print "Preparing network-based feature mapping"
        # load publishing accounts to core_accounts
        core_accounts = loadES('publishing')
        if not core_accounts:
            raise Exception('no publishing accounts')
        # load channel accounts to peri_accounts
        peri_accounts = loadES('channel')
        if not peri_accounts:
            raise Exception('no channel accounts')
        # expands core set to include first-degree followers
        self.ref_accounts = prepare_accounts(core_accounts,peri_accounts)
        # building candidate accounts
        if candidates is None:
            candidates = loadES('author',lambda d:'screen_name' not in d)
            matchsn = {a['screen_name']:0 for a in candidates}
        else:
            matchsn = {a['screen_name']:0 for a in candidates}
        if not candidates or not matchsn:
            raise Exception('no candidate accounts')
        print "Finished fetching accounts, start constructing design matrix"
        for cid,p in enumerate(candidates):
            if cid % 50 == 0:
                print cid, " candidates processed."
            tmp = namelist(p)
            for n in tmp:
                # look at the top 6 returned accounts from search API
                cand = twitter_api.search_users(n,6)
                for result in listmap_author(n, cand):
                    self.features[0].append(result[1])
                    self.features[1].append(result[2])
                    if result[0] in matchedsn:
                        self.train_labels.append(1)
                    else:
                        self.train_labels.append(-1)
                    time.sleep(5)

    def train(self):
        '''
        loads account features to train an SVM classifier
        no input- assumes one has already undergone the pain grabbing twitter data (via prepare_features)
        '''
        assert(self.train_labels,"no features for model training, run prepare_features first")
        # Obtain label matrix
        Y = np.array(self.train_labels)

        # Obtain bag of words data matrix
        #X2 = self.vectorizer.fit_transform(self.features[1])
        X = np.array(self.features[0])

        # normalize design matrix
        X1 = normalize(X,axis=0)
        #X1 = self.normalizer * np.hstack((X,X2.todense()))
        normalizer = X1[0,:]
        normalizer[normalizer>0] = normalizer[normalizer>0]/X[0,X[0,:]>0]

        if self.soft:
            self.model = SVC(C=10.0,kernel='linear', probability=True)
        else:
            self.model = LinearSVC(C=10.0)
        self.model.fit(X1,Y)
        # return trained model and trained normalizer
        return self.model, self.normalizer

    def match(self,query):
        '''
        input: query dict
        query['name'] = author name
        query['id'] = database id
        query['org'] = news organization that author belongs
        output: list
        author name, author id, author org, author JSON object
        '''
        assert(self.model,"need to either load or train SVM classifier first")
        assert(self.normalizer,"need to either load or train SVM classifier first")
        tmp = namelist(query['name'])
        for n in tmp:
            cand = twitter_user_api.search_users(n,10)
            for result in listmap_author(n, cand):
                X = np.array(result[1]).reshape((1,self.normalizer.shape[1]))
                #X2 = self.vectorizer.fit_transform([result[2]])
                #X1 = self.normalizer * np.hstack((X,X2.todense()))
                if self.soft:
                    y = self.model.decision_function(normalizer * X)
                else:
                    y = self.model.predict(normalizer * X)
                if y[0] > self.thres:
                    return [query['name'],query['id'],query['org'],user2json(cand,query)]
        return [query['name'],query['id'],query['org'],None]

    def cv_train(self,k=5,model=LinearSVC(C=10.0)):
        '''
        internal test using k-fold cross validation
        '''
        Y = np.array(self.train_labels)
        #X1 = normalize(np.hstack((np.array(self.features[0]), self.vectorizer.fit_transform(self.features[1]).todense())), axis=0)
        X1 = normalize(self.features[0])
        skf = StratifiedKFold(Y, n_folds=5)
        svm = model

        acc_svm = []
        for train_index, test_index in skf:
            svm.fit(X1[train_index], Y[train_index])
            pred = svm.predict(X1[test_index])
            acc_svm.append(accuracy_score(Y[test_index], pred, normalize=True))
            conf_svm = confusion_matrix(Y[test_index], pred)

        # print prediction accuracy
        print "Cross-validation Prediction Accuracy: ", sum(acc_svm)/5.0
        print conf_svm

        cut_idx = None
        try:
            pred = svm.decision_function(X1)
            fpr, tpr, thr = roc_curve(Y, pred)
            roc_auc = auc(fpr, tpr)
            print "Area under the ROC curve: ", roc_auc
            # search for fpr=10% cutoff score
            for idx, r in enumerate(fpr):
                if r > 0.1:
                    print "cutoff point index: ", idx," at false positive rate: ",r
                    cut_idx = idx
                    break
        except Exception:
            pass
        return cut_idx

    def update_model(self,model):
        self.model = model

def namelist(n):
    tmp = [''.join([c for c in n if ord(c)<128])]
    nametmp = remove_middle(tmp[0])
    if nametmp and nametmp != tmp[0]:
        tmp.append(nametmp)
    return tmp

if __name__ == "__main__":
    matcher = authorMatcher(soft=True)
    # try load model
    #
    matcher.

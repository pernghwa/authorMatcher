import re, datetime, math

parody_list = ['fan','fake','archive','parody','parodied','plaid','suppor',['not','real'],['not','affiliate'],'unofficial']
informal_list = ['!','?','omg','shit','fuck','stupid','fat']
journalist_terms = ['editor','journalist','writes for','write','contributor','columnist','reporter','correspondent',
                    'all views my own','all opinions my own','opinions are my own']
news_terms = ['nyt','new york times','forbes','reuters','propublica','pro publica','wsj','wall street journal',
              'washington posts','washpost','npr','national public radio','fox news','foxnews','cnn','politico',
              'buzzfeed','latimes','mcclatchy','bostonglobe','globe']
initials = ['mr','jr','jd','md','mr','ms','mrs','sr','phd','gov','sen','rep','dr']
regex = re.compile('[%s]' % re.escape(string.punctuation))

## name/string utilities ##
def remove_middle(name):
    global regex
    if len(name) <= 2:
        return ''
    return ' '.join([w for w in name.split() if len(regex.sub('', w)) > 1 and not any(map(lambda d: d == w.lower(),initials))])

def normalize_name(name):
    global regex
    if len(name) <= 2:
        return ''
    return [regex.sub('', w) for w in name.split() if len(regex.sub('', w)) > 1 and not 'jr' in w.lower()]

def compare_dict(refmap,word):
    for w in refmap:
        if edit_distance(w.lower(), word.lower())<3:
            return True
    return False

def edit_distance(s1, s2):
    if len(s1) < len(s2):
        return edit_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def ed_normalize(s1, s2):
    dis = edit_distance(s1, s2)
    tmp = len(s1)-len(s2) if len(s1)>len(s2) else 0
    return dis-tmp

# check whether journalist mentions journalist-title-related or news-org-related words
def is_journalist(text):
    ref = text.lower()
    jterms = journalist_terms+news_terms
    return any(map(lambda d:d in ref,jterms))

## feature utilities ##
def log_normalize(num):
    return math.log(1+num)

def linear_normalize(num, norm=10000):
    return float(num)/norm

def log_dec(func):
    def func_wrapper(olddata):
        return log_normalize(func(olddata))
    return func_wrapper

def linear_dec(func):
    def func_wrapper(olddata):
        return linear_normalize(func(olddata))
    return func_wrapper

# returns num of days from 2015
def datetonum(date):
    if date < datetime.datetime(2015,1,1):
        return (datetime.datetime(2015,1,1)-date).days + 1
    else:
        return 1

@linear_dec
def date_normalize(date):
    return datetonum(date)

def list_match(s, ref):
    return any(map(lambda d: d in s if type(d) is not list else all(map(lambda f: f in s,d)), ref))

# force match for multiple lists
def iterlist_match(lists, ref):
    return all(map(lambda l:list_match(l,ref),lists))

# map raw feature vector to uniform length, map bool to 0,1
def map_feature(a):
    tmp = []
    for i in a:
        if type(i) == bool:
            if i == True:
                v = 1
            else:
                v = 0
            tmp.append(v)
        else:
            tmp.append(i)
    if len(a) == 19:
        tmp.insert(10,0)
    return tmp

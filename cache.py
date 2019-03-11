from jikanpy import Jikan
from jikanpy.exceptions import APIException
import pickle
from collections import Counter, defaultdict
from time import sleep
from assoc import AssocMap


# VERBOSITY GLOBALS: changing these has no influence on performance, only the human-readable
# output of the program
NRESULTS_SEARCH = 10
NRESULTS_COMMON = 10

# PARAMETRIC GLOBALS: changing these can dramatically alter performance
API_RESET_TIME = 60 # seconds
RETRY_DELAY = 10 # seconds
MAX_ITERATIONS = API_RESET_TIME / RETRY_DELAY

def intercept(st1, sep, st2):
    if len(st1) == 0:
        return st2
    if len(st2) == 0:
        return st1
    return st1+sep+st2


class MemoCache():
    def __init__(self, j):
        self.api = j
        self.q_anime = dict()
        self.q_person = dict()
        self.q_related = defaultdict(set)
        self.q_assoc = AssocMap()

    def query_anime_chars(self, malid):
        return self.__query_anime(malid)[1]

    def query_anime(self, malid):
        return self.__query_anime(malid)[0]

    # spincycle: performs an action, attempting a fixed 
    # number of retries after fixed wait intervals,
    # giving up if the maximum allowed retries have been
    # exhausted
    def __spincycle(self, f, max_iter=MAX_ITERATIONS):
        cur_iter = 0
        while True:
            try:
                x = f()
                if cur_iter > 0:
                    print("MemoCache.__spincycle: succeeded after %d retries..." % (cur_iter))
                return x
            except APIException as api_err:
                print("MemoCache.__spincycle: APIException caught ({0})".format(api_err))
                if cur_iter >= max_iter:
                    print("MemoCache.__spincycle: no retries remaining (limit = %d)" % (max_iter))
                    raise api_err
                else:
                    cur_iter += 1
                    print("MemoCache.__spincycle: Will try again in 10 seconds (retry %d/%d)" % (cur_iter, max_iter))
                    sleep(RETRY_DELAY)

    def query_person(self, malid):
        if malid not in self.q_person:
            try:
                x = self.__spincycle(lambda: self.api.person(int(malid)))
                self.q_person[malid] = x
                self.__scan_assocs([role['anime'] for role in x['voice_acting_roles']])
            except APIException as api_err:
                print("MemoCache.query_person: failed query of person <%d>" % (int(malid)))
                return None
        else:
            x = self.q_person[malid]
        return x

    def search_anime(self, keyword, nresults=NRESULTS_SEARCH, cli_mode=False):
        try: 
            response = self.__spincycle(lambda: self.api.search('anime', str(keyword)))
            results = response['results']
            self.__scan_assocs(results)
            ret = [(x['mal_id'], x['title']) for x in results][:nresults]
            for i in range(len(ret)):
                iden, title = ret[i]
                if cli_mode:
                    print("%%%d:" % i, end=" ")
                print ("`%s`: %d\n" % (title, iden))
                yield iden
        except APIException as api_err:
            print('MemoCache.search_anime: API lookup failed for keyword <"%s">' % (keyword))

    def get_title(self, malid):
        try:
            return self.q_assoc.lookup_by_id(malid)
        except KeyError:
            return self.query_anime(malid)['title']

    def __query_anime(self, malid):
        x = None
        y = None
        if malid in self.q_anime:
            x, y = self.q_anime[malid]
            if x is None or y is None:
                print("MemoCache.__query_anime: Warn: cached result for <%d> encountered at least one query failure" % (malid))
                raise ValueError
        try:
            x = self.__spincycle(lambda: self.api.anime(int(malid)))
            y = self.__spincycle(lambda: self.api.anime(int(malid), extension='characters_staff'))
            self.q_anime[malid] = (x, y)
            self.__record(x)
        except APIException as api_err:
            print("MemoCache.__query_anime: API lookup failed for anime <%d>" % (int(malid)))
            self.q_anime[malid] = (x, y)
            raise api_err

        return x, y

    def __record(self, x):
        if x is None:
            return None
        if 'mal_id' not in x:
            return None
        if 'type' in x and x['type'] == 'manga':
            return None
        if 'title' in x:
            self.q_assoc.add_assoc(x['mal_id'], x['title'])
            return 'title'
        elif 'name' in x:
            self.q_assoc.add_assoc(x['mal_id'], x['name'])
            return 'name'


    def __scan_assocs(self, xs):
        for x in xs:
            if x is not None:
                lab = self.__record(x)
                if lab is not None:
                    yield x['mal_id'], x[lab]


    def related_deep(self, malid, init, msg=""):
        init.add(malid)
        msg = intercept(msg, "->", ("[%d]" % (malid)))
        try: 
            anime = self.query_anime(malid)
        except APIException as api_err:
            print("MemoCache.related_deep: hierarchical query failed")
            print("MemoCache.related_deep: (trace: %s)" % (msg))
            # returning 0 as a marker of failure
            return set([0])
        except ValueError:
            print("MemoCache.related_deep: Warn: cached query of anime <%d> indicates failure" % (malid))
        else:
            query = [x[0] for x in list(anime['related'].values())]
            rel = set([i for i, t in self.__scan_assocs(query)])
            blob = init.copy()
            for i in rel:
                if i not in blob:
                    blob.union(self.related_deep(i, blob, msg))
            return blob

    def query_related(self, malid):
        if malid in self.q_related:
            x = self.q_related[malid]
            if 0 in x:
                print("MemoCache.query_related: Warn: cached result for <%d> encountered at least one query failure" % (malid))
        else:
            x = self.related_deep(malid, set())
            for i in x:
                self.q_related[i] = x
        return x

    def save(self):
        with open("anime.dat", "w+b") as ani:
            pickle.dump(self.q_anime, ani)
        with open("person.dat", "w+b") as per:
            pickle.dump(self.q_person, per)
        with open("related.dat", "w+b") as rel:
            pickle.dump(self.q_related, rel)

    def restore(self, load_assocs=False):
        try:
            with open("anime.dat", "r+b") as ani:
                self.q_anime = pickle.load(ani)
            with open("person.dat", "r+b") as per:
                self.q_person = pickle.load(per)
            with open("related.dat", "r+b") as rel:
                self.q_related = pickle.load(rel)
            if load_assocs:
                self.__scan_assocs([x[0] for x in self.q_anime.values()])
        except OSError as err:
            print("OS error: {0}".format(err))

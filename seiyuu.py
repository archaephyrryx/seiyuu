from jikanpy import Jikan, exceptions.APIException
import pickle
from collections import Counter, defaultdict
from time import sleep

NRESULTS_SEARCH = 10
NRESULTS_COMMON = 10

# AssocMap: specialized data structure for associating unique IDs with the labels of their associated
#           item
class AssocMap():
    def __init__(self):
        self.id_to_label = dict()
        self.label_to_id = defaultdict(set)

    def __add_assoc(self, iden: int, label: str):
        self.id_to_label[iden] = label
        self.label_to_id[label].add(id)

    def add_assoc(self, iden: int, label: str):
        if iden not in self.id_to_label:
            self.__add_assoc(iden, label)

    def lookup_by_id(self, iden: int):
        if iden in self.id_to_label:
            return self.id_to_label[iden]
        else:
            raise KeyError

    def lookup_by_label(self, label: str):
        if label in self.label_to_id:
            return self.label_to_id[label]
        else:
            raise KeyError

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

    def __spincycle(self, f, max_iter=6):
        cur_iter = 0
        while True:
            try:
                x = f()
                return x
            except exceptions.APIException as api_err:
                print("MemoCache: API raised error, will try again in 10 seconds")
                print("({0})".format(api_err))
                if cur_iter >= max_iter:
                    raise api_err
                else:
                    cur_iter += 1
                    time.sleep(10)




    def query_person(self, malid):
        if malid not in self.q_person:
            x = self.__spincycle(lambda: self.api.person(int(malid)))
            self.q_person[malid] = x
            self.__scan_assocs([role['anime'] for role in x['voice_acting_roles']])
        else:
            x = self.q_person[malid]
        return x

    def search_anime(self, keyword, nresults=NRESULTS_SEARCH):
        response = self.__spincycle(lambda: self.api.search('anime', str(keyword)))
        results = response['results']
        for iden, title in list(self.__scan_assocs(results))[:nresults]:
            print ("`%s`: %d\n" % (title, iden))

    def get_title(self, malid):
        try:
            return self.q_assoc.lookup_by_id(malid)
        except KeyError:
            return self.query_anime(malid)['title']

    def __query_anime(self, malid):
        if malid not in self.q_anime:
            x = self.__spincycle(lambda: self.api.anime(int(malid)))
            y = self.__spincycle(lambda: self.api.anime(int(malid), extension='characters_staff'))
            self.q_anime[malid] = (x, y)
            self.__record(x)
        else:
            x, y = self.q_anime[malid]
        return x, y

    def __record(self, x):
        if 'mal_id' in x:
            if 'title' in x and x['type'] == 'anime':
                self.q_assoc.add_assoc(x['mal_id'], x['title'])
                return 'title'
            elif 'name' in x:
                self.q_assoc.add_assoc(x['mal_id'], x['name'])
                return 'name'
        return None


    def __scan_assocs(self, xs):
        for x in xs:
            lab = self.__record(x)
            if lab is not None:
                yield x['mal_id'], x[lab]


    def related_deep(self, malid, init):
        init.add(malid)
        anime = self.query_anime(malid)
        query = [x[0] for x in list(anime['related'].values())]
        rel = set([i for i, t in self.__scan_assocs(query)])
        blob = init.copy()
        for i in rel:
            if i not in blob:
                blob.union(self.related_deep(i, blob))
        return blob

    def query_related(self, malid):
        if malid not in self.q_related:
            x = self.related_deep(malid, set())
            for i in x:
                self.q_related[i] = x
        else:
            x = self.q_related[malid]
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

memo = MemoCache(Jikan())

def show_common(malid1, malid2):
    anime1 = memo.query_anime_chars(malid1)
    anime2 = memo.query_anime_chars(malid2)

    cast1 = list()
    cast2 = list()
    casta = list()
    for char in anime1['characters']:
        for va in char['voice_actors']:
            if va['language'] == 'Japanese':
                cast1.append((va['name'], char['name']))
                casta.append(va['name'])
    for char in anime2['characters']:
        for va in char['voice_actors']:
            if va['language'] == 'Japanese':
                cast2.append((va['name'], char['name']))
                casta.append(va['name'])
    for i in set(casta):
        c1 = [ch for va, ch in cast1 if va == i]
        c2 = [ch for va, ch in cast2 if va == i]
        if len(c1) * len(c2) > 0:
            print ("%s & %s (%s)\n" % (c1[0], c2[0], i))

def get_vas(malid, nresults=NRESULTS_COMMON):
    anime = memo.query_anime_chars(malid)
    rel = memo.query_related(malid)
    common = Counter()
    vas = set()
    for char in anime['characters']:
        for va in char['voice_actors']:
            if va['mal_id'] in vas:
                continue
            vas.add(va['mal_id'])
            if va['language'] == 'Japanese':
                per = memo.query_person(va['mal_id'])
                roles = [role['anime']['mal_id'] for role in per['voice_acting_roles']]
                for i in set(roles):
                    if not i == malid and i not in rel:
                        common[i] += 1
    for an, count in common.most_common(nresults):
        print ("%s (%d) @%d\n" % (memo.get_title(an), an, count))

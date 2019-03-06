from jikanpy import Jikan
import pickle
from collections import Counter, defaultdict

class MemoCache():
    def __init__(self, j):
        self.api = j
        self.q_anime = dict()
        self.q_person = dict()
        self.q_related = defaultdict(set)

    def query_anime_chars(self, malid):
        return self.__query_anime(malid)[1]

    def query_anime(self, malid):
        return self.__query_anime(malid)[0]

    def query_person(self, malid):
        if not malid in self.q_person:
            x = self.api.person(int(malid))
            self.q_person[malid] = x
        else:
            x = self.q_person[malid]
        return x
    
    def __query_anime(self, malid):
        if not malid in self.q_anime:
            x = self.api.anime(int(malid))
            y = self.api.anime(int(malid), extension='characters_staff')
            self.q_anime[malid] = (x, y)
        else:
            x, y = self.q_anime[malid]
        return x, y

    def related_deep(self, malid, init):
        init.add(malid)
        anime = self.query_anime(malid)
        query = [x[0] for x in list(anime['related'].values())]
        rel = set([q['mal_id'] for q in query if q['type'] == 'anime'])
        blob = init.copy()
        for i in rel:
            if not i in blob:
                blob.union(self.related_deep(i, blob))
        return blob


    def query_related(self, malid):
        if not malid in self.q_related:
            x = self.related_deep(malid, set())
            for i in x:
                self.q_related[i] = x
        else:
            x = self.q_related[malid]
        return x

    def save(self):
        with open("anime.dat") as ani:
            pickle.dump(self.q_anime, ani)
        with open("person.dat") as per:
            pickle.dump(self.q_person, per)
        with open("related.dat") as rel:
            pickle.dump(self.q_related, rel)

    def restore(self):
        try:
            with open("anime.dat") as ani:
                self.q_anime = pickle.load(ani)
            with open("person.dat") as per:
                self.q_person = pickle.load(per)
            with open("related.dat") as rel:
                self.q_related = pickle.load(rel)
        except OSError as err:
            print("OS error: {0}".format(err))

        

memo = MemoCache(Jikan())

def search_anime(keyword):
    response = memo.api.search('anime', str(keyword))
    results = response['results']
    for instance in results[:10]:
        print ("`%s`: %d\n" % (instance['title'], instance['mal_id']))



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

def get_vas(malid):
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
                    if not i == malid and not i in rel:
                        common[i] += 1
    for an, count in common.most_common(10):
        print ("%s (%d) @%d\n" % (memo.query_anime(an)['title'], an, count))

from jikanpy import Jikan
from collections import Counter

jikan = Jikan()

def query_anime(keyword):
    response = jikan.search('anime', str(keyword))
    results = response['results']
    for instance in results[:10]:
        print ("`%s`: %d\n" % (instance['title'], instance['mal_id']))



def show_common(malid1, malid2):
    anime1 = jikan.anime(int(malid1), extension='characters_staff')
    anime2 = jikan.anime(int(malid2), extension='characters_staff')

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
    anime = jikan.anime(int(malid), extension='characters_staff')
    common = Counter()
    rel = get_related(malid)
    vas = set()
    for char in anime['characters']:
        for va in char['voice_actors']:
            if va['mal_id'] in vas:
                continue
            vas.add(va['mal_id'])
            if va['language'] == 'Japanese':
                per = jikan.person(va['mal_id'])
                roles = [role['anime']['mal_id'] for role in per['voice_acting_roles']]
                for i in set(roles):
                    if not i == malid and not i in rel:
                        common[i] += 1
    for an, count in common.most_common(10):
        print ("%s (%d) @%d\n" % (jikan.anime(int(an))['title'], an, count))

def get_related(malid, init=list()):
    init.append(malid)
    query = [x[0] for x in list(jikan.anime(malid)['related'].values())]
    rel = [q['mal_id'] for q in query if q['type'] == 'anime']
    blob = init.copy()
    for i in rel:
        if not i in blob:
            blob.extend(get_related(i, blob))
    return [x for x in set(blob)]

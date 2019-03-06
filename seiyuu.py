from jikanpy import Jikan
from collections import Counter

jikan = Jikan()

def query_anime(keyword):
    response = jikan.search('anime', str(keyword))
    results = response['results']
    for instance in results[:5]:
        print ("`%s`: %d\n" % (instance['title'], instance['mal_id']))


def get_vas(malid):
    anime = jikan.anime(int(malid), extension='characters_staff')
    common = Counter()
    rel = get_related(malid)
    for char in anime['characters']:
        for va in char['voice_actors']:
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

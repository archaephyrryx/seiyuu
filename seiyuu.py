from jikanpy import Jikan
import pickle
from collections import Counter, defaultdict
from time import sleep
from assoc import AssocMap
from cache import MemoCache

NRESULTS_COMMON = 10

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
    print ("Character Comparison: %s (%d) & %s (%d)" % (memo.get_title(malid1), malid1, memo.get_title(malid2), malid2))
    for i in set(casta):
        c1 = [ch for va, ch in cast1 if va == i]
        c2 = [ch for va, ch in cast2 if va == i]
        if len(c1) * len(c2) > 0:
            print ("%s & %s (%s)\n" % (c1[0], c2[0], i))

def get_vas(malid, nresults=NRESULTS_COMMON, deep_check=True):
    anime = memo.query_anime_chars(malid)
    if deep_check:
        rel = memo.query_related(malid)
    else:
        rel = set([malid])
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
        yield an

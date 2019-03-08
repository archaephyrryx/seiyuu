# seiyuu
A small python script for querying anime based on common voice-actors using JikanPy.

Overview
========

`seiyuu.py` is a small python script for analyzing anime with voice actors in common, using the JikanPy interface to the MAL (MyAnimeList) API.

The scope of this program is not currently set, and it may gain new features over time.

Prerequesites
=============

The only external library that this script uses is that of JikanPy, the installation instructions for which
can be found on the library's github page.

Features
========

The script is not very sophisticated, and does not currently have any UI or CLI to speak of. In its current incarnation,
the proper usage is to open a Python REPL and bring the script into scope (`from seiyuu import *`).

The current supported features include:
  - Simple lookup of the MAL ID of shows based on search term/keyword
  - Lookup of unrelated shows with most VA's in common with query show (input as MAL ID)
  - Result-filtering to exclude shows in-franchise as they are likely to drown out interesting comparisons
  - Detailed side-by-side of characters voiced by the same VA for two query shows
  - Save/Restore of API result cache
  
The exposed top-level functions in the library do not perform API request calls directly, but instead filter requests through
a local cache that reduces the API request load by memoizing the results of all previous API lookups. This is especially
important for searches that would normally cause 429 errors due to high query volume, as it is possible to save and restore even
partial results to avoid redundant API queries.

Complexity
==========

As implemented, the number of calls required to complete a full query of shows with common VAs is proportional to the number of
voice actors in the query show, and the number of anime in the same franchise (according to MAL) as the query show. Therefore,
query shows like Detective Conan (MAL ID: 235) with a large number (>30) of related shows and a huge number (>400) of voice actors
pose a challenge to the capabilities of this script. It is, of course, possible to save whatever results could be gathered before
a 429 error is thrown by the API with `memo.save()` and load them with `memo.restore()` in a fresh REPL session, or wait 1 minute
for the API request limit to refresh and try again, but this can be potentially laborious.

Notes
=====

This script currently only considers the Japanese-language VAs for comparisons. It is not too difficult to patch in multilingual
support, but this is not currently as planned feature.

Error-handling is all-but-nonexistant, and the script does not gracefully handle any of the following scenarios:
  - Keyboard interrupt mid-query

There is limited support for catching API exceptions and retrying until timeout, but this is currently agnostic as to whether the error is a 429 error or a 404 error. As 429 indicates that repeated attempts may prove fruitful, and 404 indicates that no amount of repetitions will succeed, this distinction is currently a planned feature.
 
It is recommended that before the termination of a REPL session, `memo.save()` is run to preserve results, and `memo.restore(True)`
is run at the start of each fresh session to load the historical cache. The filenames used for reading and writing the caches
are currently hard-coded as:
  - `anime.dat` for show information
  - `person.dat` for voice-actor information
  - `related.dat` for association of shows to their entire franchise

There is a secondary database of title-id correspondences that is useful for human-legible reporting down the line,
and can even be used in some cases to bypass the need for preliminary searches for the ID corresponding to a keyword if the exact title is known. This data, however, can be inferred from the `anime.dat` contents and the `person.dat` contents, so it is not stored as a separate file but is rather recomputed. The recording process for this data is currently experimental and isn't guaranteed to work 100% of the time, but any results that are returned are authentic.

Contribution
============

As this is a hobby project, any contributions or suggestions are welcome. Feel free to use or modify this script for independent projects,
but attribution is greatly appreciated. If anyone has interest in implementing a proper UI (either CLI or web-based front-end) for this
project, please contact the project maintainer.

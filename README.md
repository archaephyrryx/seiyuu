# seiyuu
A python program for querying anime based on common voice-actors using JikanPy, coupled
with a prototype CLI frontend.

Overview
========

`seiyuu.py` is a medium-sized python backend for analyzing anime with voice actors in common, using the JikanPy interface to the MAL (MyAnimeList) API.

`cli.py` is a WIP CLI frontend for `seiyuu.py` that currently only knows how to perform simple lookups

The scope of this program is not currently set, and it may gain new features over time.

Prerequesites
=============

The only external library that `seiyuu.py` uses is that of JikanPy, the installation instructions for which
can be found on the library's github page.

`cli.py` additionally relies on the `prompt_toolkit` python library. As `cli.py` is an interface to the `seiyuu.py` library code, this is a recommended (but not strictly necessary) dependency.

Features
========

The script is fairly small, though the CLI that is currently in development may necessitate more backend features.

To use all available functions and view results in detail, the proper usage is to open a Python REPL and bring the script into scope (`from seiyuu import *`).

Though its current capabilities are somewhat limited, running `python3 cli.py` is the intended use-case in the long-term.

The current supported features include:
  - Simple lookup of the MAL ID of shows based on search term/keyword
  - Lookup of unrelated shows with most VA's in common with query show (input as MAL ID)
  - Result-filtering to exclude shows in-franchise as they are likely to drown out interesting comparisons
  - Detailed side-by-side of characters voiced by the same VA for two query shows
  - Save/Restore of API result cache
  
The exposed top-level functions in the library do not perform API request calls directly, but instead filter requests through
a local cache that reduces the API request load by memoizing the results of all previous API lookups. This is especially
important for searches that would normally cause 429 (too many requests) errors due to high query volume, as it is possible to save and restore (even
partial) results to avoid redundant API queries.

Complexity
==========

As implemented, the number of calls required to complete a full query of shows with common VAs is proportional to the number of
voice actors in the query show, and the number of anime in the same franchise (according to MAL) as the query show. Therefore,
query shows like Detective Conan (MAL ID: 235) with a large number (>30) of related shows and a huge number (>400) of voice actors
pose a challenge to the capabilities of this script. In response to such issues, the current implementation of the `cache.py` backend is designed to re-attempt any failed API query up to N times, with a wait period of M seconds between repeated attempts, where M is currently 10 and N is 6 (based on the 60-second refresh period of JikanPy MAL API queries). If the 6th retry (i.e. overall 7th attempt) is unsuccessful, the failed query records a non-response in the cache to avoid making the same doomed queries over and over again between calls or sessions. This method is used to indirectly gauge whether failed queries are caused by API overload, or whether the API responded with a 404 error.

As results are automatically loaded at the beginning of each CLI session and saved on (graceful) exit, the CLI can be slightly more user-friendly in terms of tolerating such partial progress. This effect can be partially emulated in the pure-REPL mode of execution by enclosing any API-based lookup function-stack as follows:

```python
try:
	memo.restore(True)
	# your queries here
finally:
	memo.save()
```

This ensures that, even if execution would be terminated prematurely due to an uncaught exception or a KeyboardInterrupt, the partial results collected up until said exception are saved so that repeated attempts can make incremental progress and avoid duplicating effort. This does, however, mean that potentially successful queries may be death-marked due to premature termination, which may require manual adjustment to purge stale negative results.


CLI
===

To invoke the CLI, simply run `python3 cli.py` from the command line.

The CLI offers a more seamless and intuitive experience, but not as flexible as in-REPL function calls in terms of what features are available.

The `help` command in top-level mode, and the `!help` command in sub-modes, list the full set of available commands that can be invoked currently.

The command prompt indicates the current mode or sub-mode, and any bound state associated therewith.

As the CLI is still in its relative infancy, documenting its incremental features is somewhat laborious. Once it has
reached a sufficient functionality, its usage patterns and capabilities are planned to be added to the repository wiki.

Notes
=====

This script currently only considers the Japanese-language VAs for comparisons. It is not too difficult to patch in multilingual
support, but this is not currently as planned feature.

Error-handling is complex but not comprehensive, and queries are difficult to interrupt gracefully while in progress. The CLI offers a considerable amount of cushioning to prevent runaway exceptions from crashing the script without giving it a chance to save whatever results it managed to produce.

There is limited support for catching API exceptions and retrying until timeout, but this is currently agnostic as to whether the error is a 429 error or a 404 error. As 429 indicates that repeated attempts may prove fruitful, and 404 indicates that no amount of repetitions will succeed, this distinction is currently a planned feature.
 
It is recommended that before the termination of a REPL session, `memo.save()` is run to preserve results, and `memo.restore(True)`
is run at the start of each fresh session to load the historical cache. The filenames used for reading and writing the caches
are currently hard-coded as:
  - `anime.dat` for show information
  - `person.dat` for voice-actor information
  - `related.dat` for association of shows to their entire franchise
This save/restore functionality is automatic when using the `cli.py` script as a frontend.

There is a secondary database of title-id correspondences that is useful for human-legible reporting down the line,
and can even be used in some cases to bypass the need for preliminary searches for the ID corresponding to a keyword if the exact title is known. This data, however, can be inferred from the `anime.dat` contents and the `person.dat` contents, so it is not stored as a separate file but is rather recomputed. The recording process for this data is currently experimental and isn't guaranteed to work 100% of the time, but any results that are returned are authentic.

Contribution
============

As this is a hobby project, any contributions or suggestions are welcome. Feel free to use or modify this script for independent projects,
but attribution is greatly appreciated. If anyone has interest in implementing a proper UI (either CLI or web-based front-end) for this
project, please contact the project maintainer.

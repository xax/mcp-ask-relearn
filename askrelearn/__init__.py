#!/usr/bin/env python3

from .ar_lunr import *

if __name__ == "__main__":
    import asyncio
    import sys

    from ar_base import _log
    from ar_lunr import AR_Lunr as AR_Engine

    async def main():
        BASE_URL = "http://localhost:1313"
        ar_engine = AR_Engine(BASE_URL, "searchindex.‹LANG›.json")
        await ar_engine.fetch_searchindex()

        for r in await ar_engine.ask_relearn(sys.argv[1]):
            _log.info(r)

    asyncio.run(main())

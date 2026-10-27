#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import asyncio
import logging
from pathlib import Path

from askrelearn.ar_lunr import AR_Lunr as AR_Engine

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

BASE_URL = "http://localhost:1313"
SEARCH_INDEX_PATH = "searchindex.‹LANG›.json"
DESCRIPTION = "Search for help about the given search term in the documentation provided by trhe static site builder Hugo and the Relearn theme."
CA_SITE = None
# CA_SITE = """\
# -----BEGIN CERTIFICATE-----
# …
# -----END CERTIFICATE-----
# """


@dataclass
class AppContext:
    ar_engine: AR_Engine


async def ask_relearn(ctx: AppContext, search_term: str, *, base_url: str = "") -> list[tuple[str, str]]:
    """
    Search for help about the given search term in the documentation.

    Returns a tuple containing a snippet of the found relevant information and the source URL.
    """
    return await ctx.ar_engine.ask_relearn(search_term)


async def main():
    global BASE_URL, DESCRIPTION, CA_SITE
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--description", type=str, help=f'description of topic of Relearn/Hugo site ["{DESCRIPTION}"]')
    p.add_argument("-b", "--base-url", type=str, help=f'base url of Relearn/Hugo site ["{BASE_URL}"]')
    p.add_argument(
        "-p",
        "--search-index-path",
        type=str,
        default=SEARCH_INDEX_PATH,
        help='url-path to search index JSON; ‹LANG› will be replaced by main site language variant  ["%(default)s"]',
    )
    p.add_argument("-C", "--ca-cert", type=Path, help="path to DER formatted certificate to explicitly trust")
    p.add_argument("query", type=str, help="information query")
    args = p.parse_args()

    if args.base_url is not None:
        BASE_URL = args.base_url
    if args.description is not None:
        DESCRIPTION = args.description
    if args.ca_cert is not None:
        with open(args.ca_cert, "rt") as f:
            try:
                CA_SITE = f.read()
            except:
                log.warning(f'Unable to read certificate file "{args.ca_cert}".')

    ar_engine = AR_Engine(BASE_URL, args.search_index_path, trusted_ca=CA_SITE)
    await ar_engine.fetch_searchindex()
    ctx = AppContext(ar_engine=ar_engine)

    results = await ask_relearn(ctx, args.query or "Who am I")
    for res in results:
        print(f"> {res[1]}")
        print(f": {res[0][:640]}")
        print()


if __name__ == "__main__":
    asyncio.run(main())

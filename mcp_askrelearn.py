#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (C) XA, II - X 2026.
# SPDX-License-Identifier: EUPL-1.2

import argparse
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging
from pathlib import Path
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.session import ServerSession
from mcp.types import ToolAnnotations

from askrelearn.ar_lunr import AR_Lunr as AR_Engine

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

BASE_URL = "http://localhost:1313"
SEARCH_INDEX_PATH = "searchindex.‹LANG›.json"
DESCRIPTION = "Search for help about the given search term in the documentation provided by the static site builder Hugo and the Relearn theme."

CA_SITE = None
# CA_SITE = """\
# -----BEGIN CERTIFICATE-----
# …
# -----END CERTIFICATE-----
# """


@dataclass
class AppContext:
    ar_engine: AR_Engine


@asynccontextmanager
async def app_lifespan(mcp_server: MCPServer) -> AsyncGenerator[AppContext]:
    ar_engine = AR_Engine(BASE_URL, search_index_path=SEARCH_INDEX_PATH, trusted_ca=CA_SITE)
    await ar_engine.fetch_searchindex()
    try:
        yield AppContext(ar_engine=ar_engine)
    finally:
        pass


mcp = MCPServer(name="Ask Relearn MCP", lifespan=app_lifespan)


# @mcp.tool(
#     title="AskRelearn",
#     description=DESCRIPTION,
#     annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
# )
async def ask_relearn(ctx: Context[ServerSession, AppContext], search_term: str) -> list[tuple[str, str]]:
    """
    Search for help about the given search term in the documentation.

    Returns a list of tuples containing each a snippet of the found relevant information and the source URL.
    """
    lifespan_ctx = ctx.request_context.lifespan_context
    return await lifespan_ctx.ah_engine.ask_hugo(search_term)  # pyright: ignore[reportAttributeAccessIssue]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-d", "--description", type=str, default=None, help=f'description of topic of Relearn/Hugo site ["{DESCRIPTION}"]')
    p.add_argument("-b", "--base-url", type=str, default=None, help="base url of Relearn/Hugo site")
    p.add_argument(
        "-p",
        "--search-index-path",
        type=str,
        help=f'url-path to search index JSON; ‹LANG› will be replaced by main site language variant  ["{SEARCH_INDEX_PATH}"]',
    )
    p.add_argument("-C", "--ca-cert", type=Path, help="path to DER formatted certificate to explicitly trust")
    args = p.parse_args()

    if args.base_url is not None:
        BASE_URL = args.base_url
    if args.description is not None:
        DESCRIPTION = args.description
    if args.search_index_path is not None:
        DESCRIPTION = args.description
    if args.ca_cert is not None:
        with open(args.ca_cert, "rt") as f:
            try:
                CA_SITE = f.read()
            except:
                log.warning(f'Unable to read certificate file "{args.ca_cert}".')

    ask_relearn = mcp.tool(title="AskRelearn", description=DESCRIPTION, annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))(ask_relearn)

    mcp.run(transport="stdio")

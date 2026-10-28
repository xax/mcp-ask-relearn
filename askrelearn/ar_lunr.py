#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright (C) XA, II - X 2026.
# SPDX-License-Identifier: EUPL-1.2

import json
import re
import ssl
import aiohttp
from lunr import lunr
from lunr.index import Index
from lunr.match_data import MatchData

from .ar_base import _log, Abstract_ar, ToolError

type SearchIndexEntry = dict[str, str | float | MatchData]
type SearchIndex = Index
type SearchIndex_lunr = Index


class AR_Lunr(Abstract_ar):

    async def fetch_searchindex(self):
        assert self._relearn_index_path is not None

        tls_ctx = ssl.create_default_context(cadata=self._trusted_ca)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=tls_ctx)) as session:
            if re.search("‹.?LANG›", self._relearn_index_path) != None:
                lang = "en"
                async with session.get(f"{self._base_url}") as response:
                    if response.ok:
                        index_text = await response.text()
                        _log.debug(f"Fetched index data: {index_text[1200:5000]}...")  # Log a slice
                        if (match := re.search(r'contentLangs"\s*:\s*\[\s*"(\w+)', index_text[:10000])) is not None:
                            lang = match[1]
                        else:
                            _log.warning("Failed trying to determine main language variant.")
                    else:
                        _log.error("Failed to index. Falling back to language EN")
                self._relearn_index_path = self._relearn_index_path.replace("‹.LANG›", f".{lang}")
                self._relearn_index_path = self._relearn_index_path.replace("‹LANG›", lang)

            async with session.get(f"{self._base_url}/{self._relearn_index_path}") as response:
                _log.info(f'Fetching of search index "{self._base_url}/{self._relearn_index_path}" resulted with status code {response.status}.')

                if response.status == 200:
                    relearn_index_text = await response.text()
                    _log.info(f"Fetched search index data: {relearn_index_text[:100]}...")  # Log first 100 characters
                else:
                    _log.error("Failed to fetch search index.")
                    relearn_index_text = "[{}]"

        self._relearn_index = json.loads(relearn_index_text)
        self._backend_index = lunr(
            "uri",
            fields=[
                dict(field_name="content", boost=3),
                dict(field_name="description", boost=2),
                dict(field_name="title", boost=2),
                dict(field_name="tags", extractor=lambda d: ", ".join(d)),
                dict(field_name="breadcrumb"),
            ],
            documents=self._relearn_index,
        )

    async def ask_relearn(self, search_term: str, **kwargs) -> list[tuple[str, str]]:
        await super().ask_relearn(search_term=search_term, **kwargs)
        assert self._relearn_index is not None

        results = self._backend_index.search(search_term)
        _log.debug(results[:10])

        if results is None or len(results) < 1:
            return [(search_term, "./NOT_FOUND")]

        return [
            # (await fetch_content(base_url + r.get("ref")), r.get("ref")) for r in results[:5]
            (next(filter(lambda d: d["uri"] == r["ref"], self._relearn_index))["content"], r["ref"])
            for r in results[:5]
        ]  # pyright: ignore[reportReturnType]

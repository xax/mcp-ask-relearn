#!/usr/bin/env python3

import json
import re
import ssl
import aiohttp
from rapidfuzz import process

from .ar_base import _log, Abstract_ar, ToolError

type SearchIndexEntry = dict[str, str | list[str]]
type SearchIndex = list[SearchIndexEntry]
type SearchIndex_rapidfuzz = list[SearchIndexEntry]


class AR_Rapidfuzz(Abstract_ar):

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
                    # log.info(f"Fetched search index data: {data[data.index("[", 0, 40):100]}")
                else:
                    _log.error("Failed to fetch search index.")
                    relearn_index_text = "[{}]"

        self._backend_index = json.loads(relearn_index_text)

    async def ask_relearn(self, search_term: str, **kwargs) -> list[tuple[str, str]]:
        await super().ask_relearn(search_term=search_term, **kwargs)

        results = process.extract(
            search_term,
            [
                str(entry.get("content", "")) + "\n\n" + str(entry.get("description", "")) + "\n\n" + " ".join(entry.get("tags", []))
                for entry in self._backend_index
            ],
            limit=5,
        )
        # log.debug(results[0])
        if results is None or len(results) < 1:
            return [(search_term, "./NOT_FOUND")]

        return [
            (self._backend_index[i].get("content", self._backend_index[i].get("description")), self._backend_index[i].get("uri", "./NOT_FOUND"))
            for (_i, _s, i) in results
        ]  # pyright: ignore[reportReturnType]

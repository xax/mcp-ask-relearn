#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections.abc import Buffer
import logging
from typing import Any
from mcp.server.mcpserver.exceptions import ToolError

__all__ = ("Abstract_ar",)

_log = logging.getLogger("askrelearn")


class Abstract_ar(ABC):

    _base_url: str
    _relearn_index_path: str | None
    _trusted_ca: Buffer | str | None
    _relearn_index: dict | None
    _backend_index: Any

    def __init__(self, base_url: str, search_index_path: str = "/", *, trusted_ca: Buffer | str | None = None, **kwargs):
        self._base_url = base_url
        self._relearn_index_path = search_index_path
        self._trusted_ca = trusted_ca
        self._relearn_index = None
        self._backend_index = None

    @abstractmethod
    async def fetch_searchindex(self):
        pass

    @abstractmethod
    async def ask_relearn(self, search_term: str, **_kwargs) -> list[tuple[str, str]]:
        if self._backend_index is None:
            await self.fetch_searchindex()

        return list()

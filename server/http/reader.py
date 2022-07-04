from server.http import parser

import asyncio
from typing import List, Optional


class BufferedLineReader(object):
    __slots__ = (
        "_reader",
        "_buff_size",
        "_max_header_size",
        "_max_body_chunk",
        "_lines",
        "_end_of_stream",
        "_parser",
    )

    def __init__(
        self,
        reader: asyncio.StreamReader,
        buff_size: int = 1_024,
        max_header_size: int = 1_024,
        max_body_chunk: int = 102_400,
    ) -> None:
        self._reader: asyncio.StreamReader = reader
        self._buff_size: int = buff_size
        self._max_header_size: int = max_header_size
        self._max_body_chunk: int = max_body_chunk
        self._lines: List[Optional[parser.Line]] = []
        self._end_of_stream: bool = False
        self._parser: parser.BufferedParser = parser.BufferedParser()

    async def lines(self):
        while not self._end_of_stream:
            if not self._lines:
                lines = None
                while not lines:
                    data = await self._recv()
                    lines = self._parser.maybe_get_lines(data)
                self._lines.extend(lines)

            for line in self._lines:
                yield line

    async def _recv(self):
        buffer = await self._reader.read(self._buff_size)
        if len(buffer) < self._buff_size:
            self._end_of_stream = True
        return buffer

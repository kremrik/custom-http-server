from server.error import HttpServerError
from server.http.header import Header
from server.http.method import Method
from server.http.protocol import Protocol
from server.http.parser import MessageState
from server.http.reader import BufferedLineReader

import asyncio
import logging
from collections import deque
from dataclasses import dataclass
from typing import Iterator, List, NamedTuple, Optional


LOGGER = logging.getLogger("http_parser")


class RequestParseError(HttpServerError):
    pass


class BacktrackError(HttpServerError):
    pass


@dataclass(eq=True, frozen=True)
class Request:
    method: Method
    path: str
    protocol: Protocol
    headers: Iterator[Optional[Header]]
    body: Optional[bytes]


class LazyRequest(object):
    """
    Request object that only reads from a TCP stream when
    required. For example, if no headers are interrogated,
    then parsing will stop at the Start Line.
    """

    method: Method
    path: str
    protocol: Protocol
    headers: Iterator[Optional[Header]]
    body: Optional[bytes]

    __slots__ = (
        "_reader",
        "_buff_size",
        "_state",
        "_lines",
        "_exhausted",
        "_method",
        "_path",
        "_protocol",
        "_headers",
        "_body",
    )

    def __init__(
        self,
        reader: asyncio.StreamReader,
        buff_size: int = 1024,
    ) -> None:
        self._reader: asyncio.StreamReader = reader
        self._buff_size: int = buff_size

        self._state: MessageState = MessageState.StartLine
        self._lines: BufferedLineReader = None
        self._exhausted: bool = False

        self._method: Method = None
        self._path: str = None
        self._protocol: Protocol = None
        self._headers: deque[Optional[Header]] = deque()
        self._body: deque[Optional[bytes]] = deque()

    @property
    async def method(self) -> Method:
        if not self._method:
            await self._handle_start_line()
        return self._method

    @property
    async def path(self) -> str:
        if not self._path:
            await self._handle_start_line()
        return self._path

    @property
    async def protocol(self) -> Protocol:
        if not self._protocol:
            await self._handle_start_line()
        return self._protocol

    @property
    async def headers(self) -> Iterator[Optional[Header]]:
        async for header in self._handle_headers():
            yield header

    @property
    async def body(self) -> Optional[bytes]:
        async for chunk in self._handle_body():
            yield chunk

    async def _handle_start_line(self):
        if not self._lines:
            await self._initialize_lines()

        match self._state:
            case MessageState.StartLine:
                line = await anext(self._lines)
                method, path, protocol = parse_start_line(
                    line.data.decode()
                )
                self._method = method
                self._path = path
                self._protocol = protocol

                self._state = MessageState.Header

            case MessageState.Header:
                raise BacktrackError("Start line already received")
            case MessageState.Body:
                raise BacktrackError("Start line already received")

    async def _handle_headers(self):
        if not self._lines:
            await self._initialize_lines()

        match self._state:
            case MessageState.StartLine:
                await self._handle_start_line()
                async for header in self._stream_headers():
                    yield header

            case MessageState.Header:
                if self._headers:
                    while self._headers:
                        yield self._headers.popleft()
                else:
                    async for header in self._stream_headers():
                        yield header

            case MessageState.Body:
                raise BacktrackError("Headers already received")

    async def _stream_headers(self):
        async for line in self._lines:
            if line.type == MessageState.Body:
                self._body.append(line.data)
                break
            header = parse_header(line.data.decode())
            yield header
        self._state = MessageState.Body

    async def _handle_body(self):
        if not self._lines:
            await self._initialize_lines()

        match self._state:
            case MessageState.StartLine:
                await self._handle_start_line()
                async for header in self._handle_headers():
                    self._headers.append(header)
                if self._body:
                    while self._body:
                        yield self._body.popleft()
                async for line in self._lines:
                    yield line.data

            case MessageState.Header:
                async for header in self._handle_headers():
                    self._headers.append(header)
                if self._body:
                    while self._body:
                        yield self._body.popleft()
                async for line in self._lines:
                    yield line.data

            case MessageState.Body:
                if self._exhausted:
                    raise BacktrackError("Body already received")
                if self._body:
                    while self._body:
                        yield self._body.popleft()
                async for line in self._lines:
                    yield line.data

    async def _initialize_lines(self):
        self._lines = BufferedLineReader(
            reader=self._reader,
            buff_size=self._buff_size,
        ).lines()


class StartLine(NamedTuple):
    method: Method
    path: str
    protocol: Protocol


def parse_start_line(line: str) -> StartLine:
    try:
        method, path, protocol = line.split()
        protocol = parse_protocol(protocol)
        method = parse_method(method)
        return StartLine(method, path, protocol)

    except RequestParseError as e:
        msg = "Improperly formatted HTTP start line"
        LOGGER.error(msg)
        LOGGER.debug(e)
        raise RequestParseError(msg)

    except Exception as e:
        msg = "Unknown request parsing error"
        LOGGER.error(msg)
        LOGGER.debug(e)
        raise RequestParseError(msg)


def parse_protocol(protocol: str) -> Protocol:
    try:
        return Protocol[protocol.replace(".", "_").replace("/", "")]
    except KeyError as e:
        LOGGER.error(e)
        raise RequestParseError(f"Protocol {protocol} not supported")


def parse_method(method: str) -> Method:
    try:
        return Method[method.upper()]
    except KeyError as e:
        LOGGER.error(e)
        raise RequestParseError(f"Method {method} not supported")


def parse_header(line: str) -> Header:
    try:
        name, *value = line.split(":")
        value = "".join(value)

        name = name.strip().upper()
        value = value.strip()
        header = Header(name, value)
        return header

    except Exception as e:
        msg = "Improperly formatted HTTP header"
        LOGGER.error(msg)
        LOGGER.debug(e)
        raise RequestParseError(msg)


def parse_body(
    lines: List[Optional[bytes]],
) -> Optional[bytes]:
    body = b"".join(lines)
    if not body:
        return None
    return body

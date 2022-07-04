from server.error import HttpServerError
from server.http import parser
from server.http.header import Header
from server.http.method import Method
from server.http.protocol import Protocol

import asyncio
import logging
from collections import deque
from dataclasses import dataclass
from typing import Iterator, List, NamedTuple, Optional


LOGGER = logging.getLogger("http_parser")


class RequestParseError(HttpServerError):
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
        "_parser",
        "_lines",
        "_END",
        "_msg_state",
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

        self._parser: parser.BufferedParser = parser.BufferedParser()
        self._lines: deque[parser.Line] = deque()
        self._END: bool = False
        self._msg_state: parser.MessageState = (
            parser.MessageState.StartLine
        )

        self._method: Method = None
        self._path: str = None
        self._protocol: Protocol = None
        self._headers: Iterator[Optional[Header]] = None
        self._body: Iterator[Optional[bytes]] = None

    @property
    async def method(self) -> Method:
        if not self._method:
            await self._process_next_lines()
        return self._method

    @property
    async def path(self) -> str:
        if not self._path:
            await self._process_next_lines()
        return self._path

    @property
    async def protocol(self) -> Protocol:
        if not self._protocol:
            await self._process_next_lines()
        return self._protocol

    @property
    async def headers(self) -> Iterator[Optional[Header]]:
        pass

    @property
    async def body(self) -> Optional[bytes]:
        pass


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


def parse_headers(
    lines: List[Optional[bytes]],
) -> List[Header]:
    headers = []

    try:
        for line in lines:
            name, *value = line.decode().split(":")
            value = "".join(value)

            name = name.strip().upper()
            value = value.strip()
            header = Header(name, value)
            headers.append(header)

    except Exception as e:
        msg = "Improperly formatted HTTP header"
        LOGGER.error(msg)
        LOGGER.debug(e)
        raise RequestParseError(msg)

    return headers


def parse_body(
    lines: List[Optional[bytes]],
) -> Optional[bytes]:
    body = b"".join(lines)
    if not body:
        return None
    return body

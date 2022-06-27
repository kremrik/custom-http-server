from server.error import HttpServerError
from server.http.header import Header
from server.http.method import Method
from server.http.protocol import Protocol

import asyncio
import logging
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

    def __init__(
        self, 
        reader: asyncio.StreamReader,
        buff_size: int = 1024
    ) -> None:
        self._reader: asyncio.StreamReader = reader
        self._buff_size: int = buff_size

        self._buffer: bytes = b""

        self._method: Method = None
        self._path: str = None
        self._protocol: Protocol = None
        self._headers: Iterator[Optional[Header]] = []
        self._body: Optional[bytes] = None

    @property
    async def method(self) -> Method:
        if not self._method:
            await self._parse_start_line()
        return self._method

    @property
    async def path(self) -> str:
        if not self._path:
            await self._parse_start_line()
        return self._path

    @property
    async def protocol(self) -> Protocol:
        if not self._protocol:
            await self._parse_start_line()
        return self._protocol

    @property
    async def headers(self) -> Iterator[Optional[Header]]:
        pass

    @property
    async def body(self) -> Optional[bytes]:
        pass

    async def _recv(self):
        return await self._reader.read(self._buff_size)

    async def _hydrate(self):
        self._buffer += await self._recv()

    async def _parse_start_line(self):
        if not self._buffer:
            await self._hydrate()
        
        lines = self._buffer.splitlines()
        if len(lines) == 1:
            # either there's only 1 line or it's incomplete
            await self._hydrate()

        start_line = lines[0].decode()
        
        method, path, protocol = start_line.split()
        
        if protocol == "HTTP/1.1":
            protocol = Protocol.HTTP1_1
        else:
            msg = f"Protocol {protocol} not supported"
            LOGGER.error(msg)
            raise RequestParseError(msg)

        method = Method[method.upper()]

        self._method = method
        self._path = path
        self._protocol = protocol


class StartLine(NamedTuple):
    method: Method
    path: str
    protocol: Protocol


def parse_request(message: bytes) -> Request:
    lines = message.splitlines()

    if len(lines) < 1:
        msg = "Improperly formatted HTTP message"
        detail = message if len(msg) < 497 else message[:500] + b"..."
        LOGGER.error(msg)
        LOGGER.debug(detail)
        raise RequestParseError(msg)

    start_line = lines[0]
    method, path, protocol = parse_start_line(start_line)

    _headers = []
    _body = []

    for idx, line in enumerate(lines[1:], start=1):
        if line:
            _headers.append(line)
        else:
            break

    headers = parse_headers(_headers)

    _body = lines[idx:]
    body = parse_body(_body)

    request = Request(
        method=method,
        path=path,
        protocol=protocol,
        headers=headers,
        body=body,
    )

    return request
    

def parse_start_line(line: str) -> StartLine:
    try:
        method, path, protocol = line.decode().split()
        
        if protocol == "HTTP/1.1":
            protocol = Protocol.HTTP1_1
        else:
            msg = f"Protocol {protocol} not supported"
            LOGGER.error(msg)
            raise RequestParseError(msg)

        method = Method[method.upper()]

        return StartLine(method, path, protocol)

    except Exception as e:
        msg = "Improperly formatted HTTP start line"
        LOGGER.error(msg)
        LOGGER.debug(e)
        raise RequestParseError(msg)


def parse_headers(
    lines: List[Optional[bytes]]
) -> List[Header]:
    headers = []

    try:
        for line in lines:
            name, value = line.decode().split(":")
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
    lines: List[Optional[bytes]]
) -> Optional[bytes]:
    body = b"".join(lines)
    if not body:
        return None
    return body

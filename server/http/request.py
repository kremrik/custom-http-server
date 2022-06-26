from server.error import HttpServerError
from server.http.header import Header
from server.http.method import Method
from server.http.protocol import Protocol

import logging
from dataclasses import dataclass
from typing import List, NamedTuple, Optional


LOGGER = logging.getLogger("http_parser")


class RequestParseError(HttpServerError):
    pass


@dataclass(eq=True, frozen=True)
class Request:
    method: Method
    path: str
    protocol: Protocol
    headers: List[Optional[Header]]
    body: Optional[bytes]


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

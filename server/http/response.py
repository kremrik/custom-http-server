from server.error import HttpServerError
from server.http.header import Header
from server.http.protocol import Protocol
from server.http.status import Status, STATUS_MESSAGE

from dataclasses import dataclass
from typing import List, Optional


class ResponseParseError(HttpServerError):
    pass


@dataclass(eq=True, frozen=True)
class Response:
    protocol: Protocol
    status: Status
    headers: Optional[List[Header]] = None
    body: Optional[bytes] = None

    def __post_init__(self):
        try:
            assert isinstance(self.protocol, Protocol)
            assert isinstance(self.status, Status)
            if self.headers:
                for header in self.headers:
                    assert isinstance(header, Header)
        except AssertionError as e:
            raise ResponseParseError(e)


def to_bytes(response: Response) -> bytes:
    msg = []
    status_line = make_status_line(response)
    headers = make_headers(response)
    body = make_body(response)

    msg.append(status_line)

    if headers:
        msg.append(headers)

    if body:
        msg.append(b"\n" + body)

    response_text = b"\n".join(msg)
    return response_text


def make_status_line(response: Response) -> bytes:
    protocol = response.protocol.value
    status = response.status.value
    status_message = STATUS_MESSAGE[status]
    status_line = f"{protocol} {status} {status_message}".encode()
    return status_line


def make_headers(response: Response) -> bytes:
    if response.headers:
        headers = "\n".join(
            f"{h.name}: {h.value}"
            for h in response.headers
        ).encode()
        return headers
    return None


def make_body(response: Response) -> bytes:
    return response.body

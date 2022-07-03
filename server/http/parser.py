from enum import Enum, auto
from typing import List, NamedTuple, Optional


CR = b"\r"
NL = b"\n"


class MessageState(Enum):
    StartLine = auto()
    Headers = auto()
    Body = auto()


class Line(NamedTuple):
    data: bytes
    type: MessageState


class Parser(object):
    __slots__ = (
        "_state",
        "_buffer",
        "_ws_encountered",
    )

    def __init__(self) -> None:
        self._state: MessageState = MessageState.StartLine
        self._buffer: bytes = b""
        self._ws_encountered: int = 0

    def maybe_get_line(self, data: bytes) -> Optional[List[Line]]:
        self._buffer += data
        *complete, incomplete = self._buffer.splitlines()
        self._buffer = incomplete

        lines = []
        for c in complete:
            line = Line(data=c, type=self._state)
            lines.append(line)
        return lines

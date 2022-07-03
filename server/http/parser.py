from enum import Enum, auto
from typing import List, NamedTuple, Optional


CR = b"\r"
NL = b"\n"


class MessageState(Enum):
    StartLine = auto()
    Header = auto()
    Body = auto()


class Line(NamedTuple):
    data: bytes
    type: MessageState


class BufferedParser(object):
    __slots__ = (
        "_state",
        "_buffer",
        "_ws_encountered",
    )

    def __init__(self) -> None:
        self._state: MessageState = MessageState.StartLine
        self._buffer: bytes = b""
        self._ws_encountered: int = 0

    def maybe_get_lines(self, data: bytes) -> Optional[List[Line]]:
        self._buffer += data
        *complete, incomplete = self._buffer.splitlines(
            keepends=True
        )
        self._buffer = incomplete

        lines = []
        for c in complete:
            stripped_c = c.strip()
            cur_state = self._state

            if self._state != MessageState.Body:
                ws = count_ws(c)
                self._ws_encountered += ws
                self._update_state()
                if not stripped_c:
                    continue

            line = Line(data=stripped_c, type=cur_state)
            lines.append(line)

        return lines

    def _update_state(self):
        if (
            self._state == MessageState.StartLine
            and self._ws_encountered == 2
        ):
            self._state = MessageState.Header
            self._ws_encountered = 0
        elif (
            self._state == MessageState.Header
            and self._ws_encountered == 4
        ):
            self._state = MessageState.Body
            self._ws_encountered = 0


def count_ws(line: bytes) -> int:
    return line.count(CR) + line.count(NL)

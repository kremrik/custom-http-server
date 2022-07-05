from server.http.error import HttpBaseError

from enum import Enum, auto
from typing import List, NamedTuple, Optional


CR = b"\r"
NL = b"\n"


class HeaderLengthError(HttpBaseError):
    pass


class BodyLengthError(HttpBaseError):
    pass


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
        "_max_header_size",
        "_max_body_chunk",
    )

    def __init__(
        self,
        max_header_size: int = 1_024,
        max_body_chunk: int = 102_400,
    ) -> None:
        self._max_header_size: int = max_header_size
        self._max_body_chunk: int = max_body_chunk
        self._state: MessageState = MessageState.StartLine
        self._buffer: bytes = b""

    def maybe_get_lines(self, data: bytes) -> Optional[List[Line]]:
        self._buffer += data
        *complete, incomplete = self._buffer.splitlines(
            keepends=True
        )
        if BufferedParser.incomplete_actually_complete(incomplete):
            if not complete:
                complete.append(incomplete)
                incomplete = b""
            else:
                complete[-1] += incomplete

        self._buffer = incomplete

        lines = []
        for c in complete:
            stripped_c = c.strip()
            cur_state = self._state

            match self._state:
                case MessageState.StartLine:
                    ws = BufferedParser.count_ws(c)
                    if ws == 2:
                        self._state = MessageState.Header
                    line = Line(data=stripped_c, type=cur_state)

                case MessageState.Header:
                    if not stripped_c:
                        self._state = MessageState.Body
                        continue
                    line = Line(data=stripped_c, type=cur_state)

                case MessageState.Body:
                    line = Line(data=c, type=cur_state)

            lines.append(line)

        return lines

    @staticmethod
    def count_ws(line: bytes) -> int:
        return line.count(CR) + line.count(NL)

    @staticmethod
    def incomplete_actually_complete(line: bytes) -> bool:
        return line.endswith(CR + NL)

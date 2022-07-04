from server.http import parser, reader

import unittest
from collections import deque
from textwrap import wrap
from typing import List


MOCK_RECV_SIZE = 16


class MockStreamReader:
    def __init__(self, msg: List[bytes]) -> None:
        self.chunks = deque(msg)

    async def read(self, buff_size: int):
        return self.chunks.popleft()


class test_BufferedLineReader(unittest.IsolatedAsyncioTestCase):
    async def test_start_line(self):
        data = [b"GET /path/to/resource HTTP/1.1\r\n\r\n"]
        mock_reader = MockStreamReader(data)
        blr = reader.BufferedLineReader(mock_reader)
        expect = [
            parser.Line(
                data=b"GET /path/to/resource HTTP/1.1",
                type=parser.MessageState.StartLine,
            ),
        ]

        actual = []
        async for line in blr.lines():
            actual.append(line)

        self.assertEqual(expect, actual)

    async def test_start_line_and_header(self):
        data = [
            b"GET /path/to/res",
            b"ource HTTP/1.1\r\n",
            b"Host: localhost\r",
            b"\n\r\n",
        ]
        mock_reader = MockStreamReader(data)
        blr = reader.BufferedLineReader(mock_reader, MOCK_RECV_SIZE)
        expect = [
            parser.Line(
                data=b"GET /path/to/resource HTTP/1.1",
                type=parser.MessageState.StartLine,
            ),
            parser.Line(
                data=b"Host: localhost",
                type=parser.MessageState.Header,
            ),
        ]

        actual = []
        async for line in blr.lines():
            actual.append(line)

        self.assertEqual(expect, actual)

    async def test_start_line_and_header_and_body(self):
        data = [
            b"GET /path/to/resource HTTP/1.1\r\nHost: localhost\r\n\r\nbody text\r\n\r\n",
        ]
        mock_reader = MockStreamReader(data)
        blr = reader.BufferedLineReader(mock_reader)
        expect = [
            parser.Line(
                data=b"GET /path/to/resource HTTP/1.1",
                type=parser.MessageState.StartLine,
            ),
            parser.Line(
                data=b"Host: localhost",
                type=parser.MessageState.Header,
            ),
            parser.Line(
                data=b"body text",
                type=parser.MessageState.Body,
            ),
        ]

        actual = []
        async for line in blr.lines():
            actual.append(line)
        self.assertEqual(expect, actual)

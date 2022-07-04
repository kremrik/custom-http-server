from server.http import request

import unittest
from collections import deque
from typing import List


class MockStreamReader:
    def __init__(self, chunks: List[bytes]) -> None:
        self.chunks = deque(chunks)

    async def read(self, buff_size: int):
        return self.chunks.popleft()


class test_LazyRequest(unittest.IsolatedAsyncioTestCase):
    async def test_start_line(self):
        data = [b"GET /path/to/resource HTTP/1.1\r\n\r\n"]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)

        with self.subTest("method"):
            self.assertEqual(
                request.Method.GET,
                await lazy_request.method,
            )
        with self.subTest("path"):
            self.assertEqual(
                "/path/to/resource",
                await lazy_request.path,
            )
        with self.subTest("protocol"):
            self.assertEqual(
                request.Protocol.HTTP1_1,
                await lazy_request.protocol,
            )

    async def test_start_line_HTTP1_0(self):
        data = [b"POST /path/to/resource HTTP/1.0\r\n\r\n"]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)

        with self.subTest("protocol"):
            self.assertEqual(
                request.Protocol.HTTP1_0,
                await lazy_request.protocol,
            )

    @unittest.skip("")
    async def test_header(self):
        data = [
            b"GET /path/to/resource HTTP/1.1\r\nHost: localhost\r\n\r\n"
        ]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)
        expect = [request.Header("HOST", "localhost")]
        actual = list(await lazy_request.headers)
        self.assertEqual(expect, actual)

from server.http import request

import unittest
from typing import List


class MockStreamReader:
    def __init__(self, chunks: List[bytes]) -> None:
        self.chunks = chunks
        self._pos = 0

    async def read(self, buff_size: int):
        output = self.chunks[self._pos]
        self._pos += 1
        return output


class test_LazyRequest(unittest.IsolatedAsyncioTestCase):
    async def test_start_line(self):
        data = [b"GET /path/to/resource HTTP/1.1\n\n"]
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
        data = [b"POST /path/to/resource HTTP/1.0\n\n"]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)

        with self.subTest("method"):
            self.assertEqual(
                request.Method.POST,
                await lazy_request.method,
            )
        with self.subTest("path"):
            self.assertEqual(
                "/path/to/resource",
                await lazy_request.path,
            )
        with self.subTest("protocol"):
            self.assertEqual(
                request.Protocol.HTTP1_0,
                await lazy_request.protocol,
            )

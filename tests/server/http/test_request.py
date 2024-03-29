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
                b"/path/to/resource",
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

    async def test_repeated_calls_ok(self):
        data = [b"GET /path/to/resource HTTP/1.1\r\n\r\n"]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)

        with self.subTest("method"):
            self.assertEqual(
                request.Method.GET,
                await lazy_request.method,
            )
        with self.subTest("method_again"):
            self.assertEqual(
                request.Method.GET,
                await lazy_request.method,
            )

    async def test_one_header(self):
        data = [
            b"GET /path/to/resource HTTP/1.1\r\nHost: localhost\r\n\r\n"
        ]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)
        expect = [request.Header(b"HOST", b"localhost")]
        actual = []
        async for header in lazy_request.headers:
            actual.append(header)
        self.assertEqual(expect, actual)

    async def test_mult_headers(self):
        data = [
            b"GET /path/to/resource HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\n\r\n"
        ]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)
        expect = [
            request.Header(b"HOST", b"localhost"),
            request.Header(b"CONTENT-TYPE", b"application/json"),
        ]
        actual = []
        async for header in lazy_request.headers:
            actual.append(header)
        self.assertEqual(expect, actual)

    async def test_repeated_calls_not_ok(self):
        data = [
            b"GET /path/to/resource HTTP/1.1\r\nHost: localhost\r\n\r\n"
        ]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)

        with self.subTest("initial_call_ok"):
            expect = [request.Header(b"HOST", b"localhost")]
            actual = []
            async for header in lazy_request.headers:
                actual.append(header)
            self.assertEqual(expect, actual)

        with self.subTest("next_call_fails"):
            with self.assertRaises(request.BacktrackError):
                actual = []
                async for header in lazy_request.headers:
                    actual.append(header)

    async def test_body_not_exists(self):
        data = [
            b"GET /path/to/resource HTTP/1.1\r\nHost: localhost\r\n\r\n"
        ]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)
        expect = []
        actual = []
        async for chunk in lazy_request.body:
            actual.append(chunk)
        self.assertEqual(expect, actual)

    async def test_body(self):
        data = [
            b"GET /path/to/resource HTTP/1.1\r\nHost: localhost\r\n\r\nTHIS IS\nBODY TEXT\r\n\r\n"
        ]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)
        expect = [
            b"THIS IS\n",
            b"BODY TEXT\r\n\r\n",
        ]
        actual = []
        async for chunk in lazy_request.body:
            actual.append(chunk)
        self.assertEqual(expect, actual)

    async def test_assortment(self):
        data = [
            b"".join(
                (
                    b"GET /path/to/resource HTTP/1.1\r\n",
                    b"Host: localhost\r\n",
                    b"Content-Type: application/json\r\n",
                    b"Another: foo\r\n\r\n",
                    b"THIS IS\nBODY TEXT\r\n\r\n",
                )
            )
        ]
        reader = MockStreamReader(data)
        lazy_request = request.LazyRequest(reader)

        with self.subTest("get_one_header"):
            expect = [request.Header(b"HOST", b"localhost")]
            actual = [await anext(lazy_request.headers)]
            self.assertEqual(expect, actual)

        with self.subTest("get_startline_element"):
            expect = b"/path/to/resource"
            actual = await lazy_request.path
            self.assertEqual(expect, actual)

        with self.subTest("get_next_header"):
            expect = [
                request.Header(b"CONTENT-TYPE", b"application/json")
            ]
            actual = [await anext(lazy_request.headers)]
            self.assertEqual(expect, actual)

        with self.subTest("get_body"):
            expect = [
                b"THIS IS\n",
                b"BODY TEXT\r\n\r\n",
            ]
            actual = []
            async for chunk in lazy_request.body:
                actual.append(chunk)
            self.assertEqual(expect, actual)

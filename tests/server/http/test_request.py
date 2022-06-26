from server.http import request

import unittest


class test_parse_request(unittest.TestCase):
    def test_no_headers_no_body(self):
        msg = b"GET /path/to/resource HTTP/1.1\n\n"
        expect = request.Request(
            method=request.Method.GET,
            path="/path/to/resource",
            protocol=request.Protocol.HTTP1_1,
            headers=[],
            body=None
        )
        actual = request.parse_request(msg)
        self.assertEqual(expect, actual)

    def test_one_header_no_body(self):
        msg = b"GET /path/to/resource HTTP/1.1\nAccept-Language: en\n\n"
        expect = request.Request(
            method=request.Method.GET,
            path="/path/to/resource",
            protocol=request.Protocol.HTTP1_1,
            headers=[
                request.Header("ACCEPT-LANGUAGE", "en")
            ],
            body=None
        )
        actual = request.parse_request(msg)
        self.assertEqual(expect, actual)

    def test_mult_header_no_body(self):
        msg = b"GET /path/to/resource HTTP/1.1\nHost: localhost\nAccept-Language: en\n\n"
        expect = request.Request(
            method=request.Method.GET,
            path="/path/to/resource",
            protocol=request.Protocol.HTTP1_1,
            headers=[
                request.Header("HOST", "localhost"),
                request.Header("ACCEPT-LANGUAGE", "en")
            ],
            body=None
        )
        actual = request.parse_request(msg)
        self.assertEqual(expect, actual)

    def test_body(self):
        msg = b"GET /path/to/resource HTTP/1.1\n\nTHIS IS SOME BODY TEXT"
        expect = request.Request(
            method=request.Method.GET,
            path="/path/to/resource",
            protocol=request.Protocol.HTTP1_1,
            headers=[],
            body=b"THIS IS SOME BODY TEXT"
        )
        actual = request.parse_request(msg)
        self.assertEqual(expect, actual)

    def test_assortment(self):
        msg = b"GET /path/to/resource HTTP/1.1\nHost: localhost\nAccept-Language: en\n\nTHIS IS SOME BODY TEXT"
        expect = request.Request(
            method=request.Method.GET,
            path="/path/to/resource",
            protocol=request.Protocol.HTTP1_1,
            headers=[
                request.Header("HOST", "localhost"),
                request.Header("ACCEPT-LANGUAGE", "en")
            ],
            body=b"THIS IS SOME BODY TEXT"
        )
        actual = request.parse_request(msg)
        self.assertEqual(expect, actual)
    
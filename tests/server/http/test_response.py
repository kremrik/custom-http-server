from server.http import response

import unittest


class test_parse_request(unittest.TestCase):
    def test_no_headers_no_body(self):
        protocol = response.Protocol.HTTP1_1
        status = response.Status.OK
        resp = response.Response(
            protocol=protocol,
            status=status,
        )
        expect = b"HTTP/1.1 200 OK"
        actual = response.to_bytes(resp)
        self.assertEqual(expect, actual)

    def test_headers_no_body(self):
        protocol = response.Protocol.HTTP1_1
        status = response.Status.OK
        resp = response.Response(
            protocol=protocol,
            status=status,
            headers=[
                response.Header("Content-Type", "application/json")
            ],
        )
        expect = b"HTTP/1.1 200 OK\nContent-Type: application/json"
        actual = response.to_bytes(resp)
        self.assertEqual(expect, actual)

    def test_headers_body(self):
        protocol = response.Protocol.HTTP1_1
        status = response.Status.OK
        resp = response.Response(
            protocol=protocol,
            status=status,
            headers=[
                response.Header("Content-Type", "application/json")
            ],
            body=b"THIS IS A MESSAGE",
        )
        expect = b"HTTP/1.1 200 OK\nContent-Type: application/json\n\nTHIS IS A MESSAGE"
        actual = response.to_bytes(resp)
        self.assertEqual(expect, actual)

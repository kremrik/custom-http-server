from server.http import parser

import unittest


class test_Parser(unittest.TestCase):
    def test_line_and_buffer_same_size(self):
        line = b"GET / HTTP/1.1\r\n\r\n"
        p = parser.BufferedParser()

        expect = [
            parser.Line(
                data=b"GET / HTTP/1.1",
                type=parser.MessageState.StartLine,
            )
        ]
        actual = p.maybe_get_lines(line)

        self.assertEqual(expect, actual)

    def test_line_divided_by_text(self):
        line1 = b"GET / HTT"
        line2 = b"P/1.1\r\n\r\n"

        p = parser.BufferedParser()

        with self.subTest("should_return_none"):
            expect = []
            actual = p.maybe_get_lines(line1)
            self.assertEqual(expect, actual)

        with self.subTest("should_return_line"):
            expect = [
                parser.Line(
                    data=b"GET / HTTP/1.1",
                    type=parser.MessageState.StartLine,
                )
            ]
            actual = p.maybe_get_lines(line2)
            self.assertEqual(expect, actual)

    def test_start_line_and_header_within_buffer(self):
        line = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        p = parser.BufferedParser()
        expect = [
            parser.Line(
                data=b"GET / HTTP/1.1",
                type=parser.MessageState.StartLine,
            ),
            parser.Line(
                data=b"Host: localhost",
                type=parser.MessageState.Header,
            ),
        ]
        actual = p.maybe_get_lines(line)
        self.assertEqual(expect, actual)

    def test_start_line_and_header_and_body_within_buffer(self):
        line = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\nBODY\nTEXT\r\n\r\n"
        p = parser.BufferedParser()
        expect = [
            parser.Line(
                data=b"GET / HTTP/1.1",
                type=parser.MessageState.StartLine,
            ),
            parser.Line(
                data=b"Host: localhost",
                type=parser.MessageState.Header,
            ),
            parser.Line(
                data=b"BODY",
                type=parser.MessageState.Body,
            ),
            parser.Line(
                data=b"TEXT",
                type=parser.MessageState.Body,
            ),
        ]
        actual = p.maybe_get_lines(line)
        self.assertEqual(expect, actual)

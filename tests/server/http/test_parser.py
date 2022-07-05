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
                data=b"BODY\n",
                type=parser.MessageState.Body,
            ),
            parser.Line(
                data=b"TEXT\r\n\r\n",
                type=parser.MessageState.Body,
            ),
        ]
        actual = p.maybe_get_lines(line)
        self.assertEqual(expect, actual)

    def test_start_line_and_header_broken_up(self):
        lines = [
            b"GET /path/to/resource HTTP/1.1\r",
            b"\nHost: localhost\r\n\r\n",
        ]
        p = parser.BufferedParser()

        with self.subTest("not_enough_data_yet"):
            expect = []
            actual = p.maybe_get_lines(lines[0])
            self.assertEqual(expect, actual)

        with self.subTest("now_we_have_enough"):
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
            actual = p.maybe_get_lines(lines[1])
            self.assertEqual(expect, actual)

    def test_start_line_header_broken_up_2(self):
        lines = [
            b"GET /path/to/res",
            b"ource HTTP/1.1\r\n",
            b"Host: localhost\r",
            b"\n\r\n",
        ]
        p = parser.BufferedParser()

        with self.subTest("not_enough_data_yet"):
            expect = []
            actual = p.maybe_get_lines(lines[0])
            self.assertEqual(expect, actual)

        with self.subTest("enough_for_start_line"):
            expect = [
                parser.Line(
                    data=b"GET /path/to/resource HTTP/1.1",
                    type=parser.MessageState.StartLine,
                ),
            ]
            actual = p.maybe_get_lines(lines[1])
            self.assertEqual(expect, actual)

        with self.subTest("not_enough_data_again"):
            expect = []
            actual = p.maybe_get_lines(lines[2])
            self.assertEqual(expect, actual)

        with self.subTest("header_now"):
            expect = [
                parser.Line(
                    data=b"Host: localhost",
                    type=parser.MessageState.Header,
                ),
            ]
            actual = p.maybe_get_lines(lines[3])
            self.assertEqual(expect, actual)

    def test_start_line_header_body_broken_up(self):
        lines = [
            b"GET /path/to/resource HTTP/1.1\r",
            b"\nHost: localhost",
            b"\r\n\r\nbody text\r\n\r\n",
        ]
        p = parser.BufferedParser()

        with self.subTest("not_enough_data_yet"):
            expect = []
            actual = p.maybe_get_lines(lines[0])
            self.assertEqual(expect, actual)

        with self.subTest("enough_for_start_line"):
            expect = [
                parser.Line(
                    data=b"GET /path/to/resource HTTP/1.1",
                    type=parser.MessageState.StartLine,
                ),
            ]
            actual = p.maybe_get_lines(lines[1])
            self.assertEqual(expect, actual)

        with self.subTest("header_and_body_now"):
            expect = [
                parser.Line(
                    data=b"Host: localhost",
                    type=parser.MessageState.Header,
                ),
                parser.Line(
                    data=b"body text\r\n\r\n",
                    type=parser.MessageState.Body,
                ),
            ]
            actual = p.maybe_get_lines(lines[2])
            self.assertEqual(expect, actual)

    def test_body_with_newline(self):
        lines = [
            b"GET /path/to/resource HTTP/1.1\r",
            b"\nHost: localhost",
            b"\r\n\r\nBODY\n    TEXT\r\n\r\n",
        ]
        p = parser.BufferedParser()

        with self.subTest("not_enough_data_yet"):
            expect = []
            actual = p.maybe_get_lines(lines[0])
            self.assertEqual(expect, actual)

        with self.subTest("enough_for_start_line"):
            expect = [
                parser.Line(
                    data=b"GET /path/to/resource HTTP/1.1",
                    type=parser.MessageState.StartLine,
                ),
            ]
            actual = p.maybe_get_lines(lines[1])
            self.assertEqual(expect, actual)

        with self.subTest("header_and_body_now"):
            expect = [
                parser.Line(
                    data=b"Host: localhost",
                    type=parser.MessageState.Header,
                ),
                parser.Line(
                    data=b"BODY\n", type=parser.MessageState.Body
                ),
                parser.Line(
                    data=b"    TEXT\r\n\r\n",
                    type=parser.MessageState.Body,
                ),
            ]
            actual = p.maybe_get_lines(lines[2])
            self.assertEqual(expect, actual)

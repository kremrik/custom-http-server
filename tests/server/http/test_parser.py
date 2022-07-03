from server.http import parser

import unittest


class test_Parser(unittest.TestCase):
    def test_line_and_buffer_same_size(self):
        line = b"GET / HTTP/1.1\r\n\r\n"
        p = parser.Parser()

        expect = [
            parser.Line(
                data=b"GET / HTTP/1.1",
                type=parser.MessageState.StartLine,
            )
        ]
        actual = p.maybe_get_line(line)

        self.assertEqual(expect, actual)

    def test_line_divided_by_text(self):
        line1 = b"GET / HTT"
        line2 = b"P/1.1\r\n\r\n"

        p = parser.Parser()

        with self.subTest("should_return_none"):
            expect = []
            actual = p.maybe_get_line(line1)
            self.assertEqual(expect, actual)

        with self.subTest("should_return_line"):
            expect = [
                parser.Line(
                    data=b"GET / HTTP/1.1",
                    type=parser.MessageState.StartLine,
                )
            ]
            actual = p.maybe_get_line(line2)
            self.assertEqual(expect, actual)

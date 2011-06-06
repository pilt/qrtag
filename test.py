# coding=utf-8
import unittest
from random import sample, choice
from string import letters
import os

from qrtag import QRCode
from qrtag import Sticker
from qrtag import PDFMaker

class QRCodeTest(unittest.TestCase):
    text = "foobar"
    size = 50

    def setUp(self):
        self.qr = QRCode(self.text, self.size)

    def test_build(self):
        version, size, img = self.qr.build()
        self.assertEqual(size, self.size)
        self.assertTrue(hasattr(img, 'save'))


class StickerTest(unittest.TestCase):
    code = "code"
    line = "line"

    def setUp(self):
        self.sticker = Sticker(self.code, self.line)

    def test_build(self):
        """Make sure image can be built, that it is quadratic, and verify its
        size.
        """
        img = self.sticker.build()
        self.assertTrue(hasattr(img, 'save'))
        s1, s2 = img.size
        self.assertTrue(s1 == s2)
        self.assertTrue(s1 >= self.sticker.want_size)
        self.assertTrue(s2 >= self.sticker.want_size)


class PDFMakerTest(unittest.TestCase):
    sticker_count = 100
    code_length = 25
    out_file = 'pdfmakertest.pdf'
    first_names = [
        'Simon',
        'Åsa',
        'Torbjörn',
        'Gåsa',
        'Lännart',
        'Älin',
        'Örban',
    ]
    last_names = [
        'Anderssån',
        'Erikssån',
        'Svänzzon',
        'Örnvinge',
        'Ågren',
        'Silversköld',
    ]

    def setUp(self):
        codes = ['http://twitter.com/' + "".join(sample(letters, self.code_length)) for dummy 
                in range(self.sticker_count)]
        lines = [choice(self.first_names) + ' ' + choice(self.last_names) for dummy 
                in range(self.sticker_count)]

        stickers = [Sticker(c, l) for c, l in zip(codes, lines)]
        self.maker = PDFMaker(self.out_file, stickers)

    def test_build(self):
        """Make sure that the out file exists and that it is a PDF file."""
        self.maker.build()
        self.assertTrue(os.path.isfile(self.out_file))
        with open(self.out_file, 'r') as f:
            header_line = f.readlines()[0]
            self.assertTrue(header_line.startswith('%PDF-'))


if __name__ == '__main__':
    unittest.main()

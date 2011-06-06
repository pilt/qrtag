# coding=utf-8
import os
from tempfile import mkstemp

from reportlab.platypus import PageTemplate, BaseDocTemplate, Frame
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, NextPageTemplate
from reportlab.platypus import PageBreak
from reportlab.platypus import Image as PDFImage # no confusion with PIL's Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import TA_CENTER
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm, mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

import qrencode

pdfmetrics.registerFont(TTFont('GoodDog', 'GoodDog.ttf'))

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
PAD = 1.25 * cm
INNER_WIDTH = PAGE_WIDTH - 2 * PAD

styles = getSampleStyleSheet()
line_style = ParagraphStyle(
    name="LineStyle",
    alignment=TA_CENTER,
    firstLineIndent=0,
    leftIndent=0,
    rightIndent=0,
    fontName="GoodDog",
    fontSize=60,
    spaceBefore=1.65 * PAD, # FIXME: finely tuned
    spaceAfter=PAD,
)

class QRCode(object):

    def __init__(self, code, size):
        self.code = code
        self.size = size

    def build(self):
        """Wraps `qrencode.encode`."""
        return qrencode.encode_scaled(
            data=self.code,
            hint=qrencode.QR_MODE_8,
            case_sensitive=True,
            version=0, # FIXME: should possibly be fixed
            size=self.size,
        )


class Sticker(object):
    want_size = 1

    def __init__(self, code, line):
        self.code = code
        self.line = line

    def build(self):
        """Return `PIL.Image` of QR code."""
        version, got_size, image = QRCode(self.code, self.want_size).build()
        return image


class BackgroundTemplate(PageTemplate):
    def __init__(self, pdf_template_filename, name=None):
        frames = [Frame(
            PAD,
            PAD,
            PAGE_WIDTH - 2 * PAD,
            PAGE_HEIGHT - 2 * PAD,
            )]
        PageTemplate.__init__(self, name, frames)
        # use first page as template
        page = PdfReader(pdf_template_filename, decompress=False).pages[0]
        self.page_template = pagexobj(page)
        # Scale it to fill the complete page
        self.page_xscale = PAGE_WIDTH/self.page_template.BBox[2]
        self.page_yscale = PAGE_HEIGHT/self.page_template.BBox[3]

    def beforeDrawPage(self, canvas, doc):
        """Draws the background before anything else"""
        canvas.saveState()
        rl_obj = makerl(canvas, self.page_template)
        canvas.scale(self.page_xscale, self.page_yscale)
        canvas.doForm(rl_obj)
        canvas.restoreState()


class TagDocTemplate(SimpleDocTemplate):
    pass


class PDFMaker(object):

    def __init__(self, out_file, stickers, template=None):
        self.out_file = out_file
        self.stickers = stickers
        self.template = template

    def build(self):
        doc = TagDocTemplate(self.out_file)
        doc.addPageTemplates([BackgroundTemplate(
            'qringly.pdf', name='background')])

        story = []
        style = styles['Normal']
        
        # FIXME: The tempfiles are handled in an ugly manner.
        tempfiles = []
        for sticker in self.stickers:
            try:
                handle, tmp = mkstemp('_qrtag.png')
                os.close(handle)
                img = sticker.build()
                img.save(tmp, 'png')
                scaled_size = INNER_WIDTH - 4 * PAD
                story.append(NextPageTemplate('background'))
                qr_img = PDFImage(tmp, width=scaled_size, height=scaled_size)
                qr_img.hAlign = 'CENTER'
                story.append(Spacer(INNER_WIDTH, 2 * PAD))
                story.append(qr_img)
                story.append(Paragraph(sticker.line, line_style))
                story.append(PageBreak())
            finally:
                tempfiles.append(tmp)

        doc.build(story)
        for tmp in tempfiles:
            os.remove(tmp)

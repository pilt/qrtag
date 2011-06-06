# coding=utf-8
from distutils.core import setup

setup(
    name='qrtag',
    version='0.1',
    py_modules=['qrtag'],
    requires=['pyqrencode', 'PIL', 'reportlab'],
)

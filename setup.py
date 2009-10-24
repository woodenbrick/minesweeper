#!/usr/bin/python

from DistUtilsExtra.command import *
from distutils.core import setup
import os
import glob 

PROGRAM_NAME = 'minesweeper'
VERSION = '0.01'

images = glob.glob(os.path.join("images", "*.png"))
desc = """Clone of the popular game"""
long_desc = """Useful procrastination tool"""
setup ( name = PROGRAM_NAME,
        version = VERSION,
        description = desc,
        long_description = long_desc,
        author = 'Daniel Woodhouse',
        author_email = 'wodemoneke@gmail.com',
	    license = 'GPLv3',
        platforms = ['Linux'],
        url = 'http://github.com/woodenbrick/minesweeper/tree',
        packages = ['minesweeper'],
        data_files = [
            ('share/applications/', ['mtp-lastfm.desktop']),
            ('share/minesweeper/images/', images),
            ('bin/', ['minesweeper'])]
)

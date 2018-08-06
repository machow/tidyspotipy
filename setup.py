#!/usr/bin/env python

import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('tidyspotify.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
	name = 'tidyspotify',
	version = version,
	py_modules= ['tidyspotify'],
	install_requires = ['spotipy'],
        description = 'tidy wrapper around spotipy library',
        author = 'Michael Chow',
        author_email = 'michael@datacamp.com',
        url = 'https://github.com/machow/tidyspotify')

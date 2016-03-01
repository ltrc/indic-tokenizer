#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os.path
import warnings
from setuptools import setup

try:
    setuptools_available = True
except ImportError:
    from distutils.core import setup
    setuptools_available = False

try:
    import py2exe
except ImportError:
    if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
        print("Cannot import py2exe", file=sys.stderr)
        exit(1)

py2exe_options = {
    "bundle_files": 1,
    "compressed": 1,
    "optimize": 2,
    "dist_dir": '.',
    "dll_excludes": ['w9xpopen.exe'],
}

py2exe_console = [{
    "script": "./irtokz/__main__.py",
    "dest_base": "irtokz",
}]

py2exe_params = {
    'console': py2exe_console,
    'options': {"py2exe": py2exe_options},
    'zipfile': None
}

if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
    params = py2exe_params
else:
    files_spec = [
        ('share/doc/irtokz', ['README.rst'])
    ]
    root = os.path.dirname(os.path.abspath(__file__))
    data_files = []
    for dirname, files in files_spec:
        resfiles = []
        for fn in files:
            if not os.path.exists(fn):
                warnings.warn('Skipping file %s since it is not present. Type  make  to build all automatically generated files.' % fn)
            else:
                resfiles.append(fn)
        data_files.append((dirname, resfiles))

    params = {
        'data_files': data_files,
    }
    params['entry_points'] = {'console_scripts': ['ind-tokz = irtokz:ind_main', 'rom-tokz = irtokz:rom_main']}

# Get package version 
exec(compile(open('irtokz/version.py').read(),
             'irtokz/version.py', 'exec'))

setup(
    name = "indic-tokenizer",
    version = __version__,
    description='Tokenizer for Indian languages (scripts) and Roman',
    long_description = open('README.rst', 'rb').read().decode('utf8'),
    author='Irshad Ahmad Bhat',
    author_email='irshad.bhat@research.iiit.ac.in',
    maintainer='Irshad Ahmad Bhat',
    maintainer_email='irshad.bhat@research.iiit.ac.in',
    url='https://github.com/irshadbhat/indic-tokenizer',
    download_url='https://github.com/irshadbhat/indic-tokenizer/archive/master.zip',
    license='MIT',
    keywords=['Tokenizer', 'Linguistics', 'NLP'],
    platforms=['any'],
    packages=['irtokz'],
    package_dir={'irtokz':'irtokz'},
    package_data={'irtokz': ['data/*']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console'
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic'
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],

    **params
)

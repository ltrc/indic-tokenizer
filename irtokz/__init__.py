#!/usr/bin/env python 
# -*- coding: utf-8 -*-

"""Tokenizer for Indian scripts and Roman script.

This module provides a complete tokenizer for Indian languages including 
Urdu and Kashmiri and Roman script.

Copyright (c) 2015-2016 Irshad Ahmad <irshad.bhat@research.iiit.ac.in>

Distributed under MIT license [http://opensource.org/licenses/mit-license.html].
"""

from __future__ import print_function

__name__       = "Indic Tokenizer"
__author__     = "Irshad Ahmad"
__copyright__  = "Copyright (C) 2015-16 Irshad Ahmad"
__version__    = "1.0"
__license__    = "MIT"
__maintainer__ = "Irshad Ahmad"
__email__      = "irshad.bhat@research.iiit.ac.in"
__status__     = "Beta"
__all__        = ["indic_tokenize", "roman_tokenize"]

import sys
import argparse

from indic_tokenize import tokenize_ind
from roman_tokenize import tokenize_rom

def ind_main():
    lang_help = """select language (3 letter ISO-639 code)
        Hindi       : hin
        Urdu        : urd
        Telugu      : tel
        Tamil       : tam
        Malayalam   : mal
        Kannada     : kan
        Bengali     : ben
        Oriya       : ori
        Punjabi     : pan
        Marathi     : mar
        Nepali      : nep
        Gujarati    : guj
        Bodo        : bod
        Konkani     : kok
        Assamese    : asm
        Kashmiri    : kas"""
    languages = "hin urd ben asm guj mal pan tel tam kan ori mar nep bod kok kas".split()
    # parse command line arguments 
    parser = argparse.ArgumentParser(prog="indic_tokenizer",
                                    description="Tokenizer for Indian Scripts",
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--i', metavar='input', dest="INFILE", type=argparse.FileType('r'), default=sys.stdin, help="<input-file>")
    parser.add_argument('--l', metavar='language', dest="lang", choices=languages, default='hin', help=lang_help)
    parser.add_argument('--s', dest='split_sen', action='store_true', help="set this flag to apply sentence segmentation")
    parser.add_argument('--o', metavar='output', dest="OUTFILE", type=argparse.FileType('w'), default=sys.stdout, help="<output-file>")
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenize_ind(lang=args.lang, split_sen=args.split_sen)
    # convert data
    for line in args.INFILE:
        line = tzr.tokenize(line)
        args.OUTFILE.write('%s\n' %line)

    # close files 
    args.INFILE.close()
    args.OUTFILE.close()

def rom_main():
    # parse command line arguments 
    parser = argparse.ArgumentParser(prog="roman_tokenizer", description="Tokenizer for Roman-Script")
    parser.add_argument('--i', metavar='input', dest="INFILE", type=argparse.FileType('r'), default=sys.stdin, help="<input-file>")
    parser.add_argument('--s', dest='split_sen', action='store_true', help="set this flag to apply sentence segmentation")
    parser.add_argument('--o', metavar='output', dest="OUTFILE", type=argparse.FileType('w'), default=sys.stdout, help="<output-file>")
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenize_rom(split_sen=args.split_sen)
    # convert data
    for line in args.INFILE:
        line = tzr.tokenize(line)
        args.OUTFILE.write('%s\n' %line)

    # close files 
    args.INFILE.close()
    args.OUTFILE.close()

#def main():
#    rom_main()

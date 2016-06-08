#!/usr/bin/env python
# -*- coding=utf-8 -*-

import re
import os
import sys
import argparse


class tokenize_rom():

    def __init__(self, split_sen=False):
        self.split_sen = split_sen
        file_path = os.path.abspath(__file__).rpartition('/')[0]

        self.NBP = dict()
        with open('%s/data/NONBREAKING_PREFIXES' % file_path) as fp:
            for line in fp:
                if line.startswith('#'):
                    continue
                if '#NUMERIC_ONLY#' in line:
                    self.NBP[line.replace('#NUMERIC_ONLY#', '').split()[0]] = 2
                else:
                    self.NBP[line.strip()] = 1

        # precompile regexes
        self.fit()

    def fit(self):
        # junk characters
        self.junk = re.compile(r'[\x00-\x1f]')
        # Latin-1 supplementary characters
        self.latin = re.compile(ur'([\xa1-\xbf\xd7\xf7])')
        # general unicode punctituations except "’"
        self.upunct = re.compile(ur'([\u2012-\u2018\u201a-\u206f])')
        # unicode mathematical operators
        self.umathop = re.compile(ur'([\u2200-\u2211\u2213-\u22ff])')
        # unicode fractions
        self.ufrac = re.compile(ur'([\u2150-\u2160])')
        # unicode superscripts and subscripts
        self.usupsub = re.compile(ur'([\u2070-\u209f])')
        # unicode currency symbols
        self.ucurrency = re.compile(ur'([\u20a0-\u20cf])')
        # all "other" ASCII special characters
        self.specascii = re.compile(r'([\\!@#$%^&*()_+={\[}\]|";:<>?`~/])')

        # keep multiple dots together
        self.multidot = re.compile(r'(\.\.+)([^\.])')
        # seperate "," outside
        self.notanumc = re.compile(r'([^0-9]),')
        self.cnotanum = re.compile(r',([^0-9])')
        # split contractions right (both "'" and "’")
        self.numcs = re.compile(ur"([0-9])(['\u2019])s")
        self.aca = re.compile(
            ur"([a-zA-Z\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])")
        self.acna = re.compile(
            ur"([a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])")
        self.nacna = re.compile(
            ur"([^a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])")
        self.naca = re.compile(
            ur"([^a-zA-Z0-9\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])")

        # multiple hyphens
        self.multihyphen = re.compile(r'(-+)')
        self.hypheninnun = re.compile(r'(-?[0-9]-+[0-9]-?){,}')
        # restore multi-dots
        self.restoredots = re.compile(r'(DOT)(\1*)MULTI')

        # split sentences
        if self.split_sen:
            self.splitsenr1 = re.compile(ur' ([.?]) ([A-Z])')
            self.splitsenr2 = re.compile(ur' ([.?]) ([\'" ]+) ([A-Z])')
            self.splitsenr3 = re.compile(ur' ([.?]) ([\u201c\u2018 ]+ [A-Z])')
            self.splitsenr4 = re.compile(
                ur' ([.?]) ([\'"\)\}\]\u2019\u201d> ]+) ([A-Z])')

    def tokenize(self, text):
        text = text.decode('utf-8', errors='ignore')
        text = text.split()
        text = ' '.join(text)
        text = ' %s ' % (text)
        # seperate out on Latin-1 supplementary characters
        text = self.latin.sub(r' \1 ', text)
        # seperate out on general unicode punctituations except "’"
        text = self.upunct.sub(r' \1 ', text)
        # seperate out on unicode mathematical operators
        text = self.umathop.sub(r' \1 ', text)
        # seperate out on unicode fractions
        text = self.ufrac.sub(r' \1 ', text)
        # seperate out on unicode superscripts and subscripts
        text = self.usupsub.sub(r' \1 ', text)
        # seperate out on unicode currency symbols
        text = self.ucurrency.sub(r' \1 ', text)

        text = text.encode('utf-8')
        # remove ascii junk
        text = self.junk.sub('', text)
        # seperate out all "other" ASCII special characters
        text = self.specascii.sub(r' \1 ', text)

        # keep multiple dots together
        text = self.multidot.sub(lambda m: r' %sMULTI %s' % (
            'DOT' * len(m.group(1)), m.group(2)), text)
        # seperate "," outside
        text = self.notanumc.sub(r'\1 , ', text)
        text = self.cnotanum.sub(r' , \1', text)

        text = text.decode('utf-8')
        # split contractions right (both "'" and "’")
        text = self.nacna.sub(r"\1 \2 \3", text)
        text = self.naca.sub(r"\1 \2 \3", text)
        text = self.acna.sub(r"\1 \2 \3", text)
        text = self.aca.sub(r"\1 \2\3", text)
        text = self.numcs.sub(r"\1 \2s", text)

        text = text.encode('utf-8')
        text = text.replace("''", " ' ' ")

        # handle non-breaking prefixes
        words = text.split()
        text_len = len(words) - 1
        text = str()
        for i, word in enumerate(words):
            if word.endswith('.'):
                dotless = word[:-1]
                if dotless.isdigit():
                    word = dotless + ' .'
                elif ('.' in dotless and re.search('[a-zA-Z]', dotless)) or \
                        self.NBP.get(dotless, 0) == 1 or \
                        (i < text_len and words[i + 1][0].islower()):
                    pass
                elif self.NBP.get(dotless, 0) == 2 and \
                        (i < text_len and words[i + 1][0].isdigit()):
                    pass
                elif i < text_len and words[i + 1][0].isdigit():
                    pass
                else:
                    word = dotless + ' .'
            text += "%s " % word

        # seperate out hyphens
        text = self.multihyphen.sub(lambda m: r'%s' %
                                    (' '.join('-' * len(m.group(1)))), text)
        text = self.hypheninnun.sub(
            lambda m: r'%s' %
            (m.group().replace(
                '-', ' - ')), text)
        text = text.split()
        text = ' '.join(text)
        # restore multi-dots
        text = self.restoredots.sub(lambda m: r'.%s' %
                                    ('.' * (len(m.group(2)) / 3)), text)

        # split sentences
        if self.split_sen:
            text = self.splitsenr1.sub(r' \1\n\2', text)
            text = self.splitsenr2.sub(r' \1\n\2 \3', text)
            text = text.decode('utf-8')
            text = self.splitsenr3.sub(r' \1\n\2', text)
            text = self.splitsenr4.sub(r' \1 \2\n\3', text)
            text = text.encode('utf-8')

        return text

if __name__ == '__main__':

    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog="roman_tokenizer",
        description="Tokenizer for Roman-Scripts")
    parser.add_argument(
        '--i',
        metavar='input',
        dest="INFILE",
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="<input-file>")
    parser.add_argument(
        '--s',
        dest='split_sen',
        action='store_true',
        help="set this flag for splittting on sentence boundaries")
    parser.add_argument(
        '--o',
        metavar='output',
        dest="OUTFILE",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="<output-file>")
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenize_rom(split_sen=args.split_sen)
    # convert data
    for line in args.INFILE:
        line = tzr.tokenize(line)
        args.OUTFILE.write('%s\n' % line)

    # close files
    args.INFILE.close()
    args.OUTFILE.close()

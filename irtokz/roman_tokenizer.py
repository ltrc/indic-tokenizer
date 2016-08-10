#!/usr/bin/env python
# -*- coding=utf-8 -*-

from __future__ import (division, unicode_literals)

import re
import os


class RomanTokenizer():

    def __init__(self, split_sen=False):
        self.split_sen = split_sen
        file_path = os.path.abspath(__file__).rpartition('/')[0]

        self.NBP = dict()
        with open('%s/data/NONBREAKING_PREFIXES' % file_path) as fp:
            for line in fp:
                if line.startswith('#'):
                    continue
                if '#NUMERIC_ONLY#' in line:
                    line = line.replace('#NUMERIC_ONLY#', '').split()[0]
                    self.NBP[line] = 2
                else:
                    self.NBP[line.strip()] = 1

        # precompile regexes
        self.fit()

    def fit(self):
        # junk characters
        self.junk = re.compile(r'[\x00-\x1f]')
        # Latin-1 supplementary characters
        self.latin = re.compile(r'([\xa1-\xbf\xd7\xf7])')
        # general unicode punctituations except "’"
        self.upunct = re.compile(r'([\u2012-\u2018\u201a-\u206f])')
        # unicode mathematical operators
        self.umathop = re.compile(r'([\u2200-\u2211\u2213-\u22ff])')
        # unicode fractions
        self.ufrac = re.compile(r'([\u2150-\u2160])')
        # unicode superscripts and subscripts
        self.usupsub = re.compile(r'([\u2070-\u209f])')
        # unicode currency symbols
        self.ucurrency = re.compile(r'([\u20a0-\u20cf])')
        # all "other" ASCII special characters
        self.specascii = re.compile(r'([\\!@#$%^&*()_+={\[}\]|";:<>?`~/])')

        # keep multiple dots together
        self.multidot = re.compile(r'(\.\.+)([^\.])')
        # seperate "," outside
        self.notanumc = re.compile(r'([^0-9]),')
        self.cnotanum = re.compile(r',([^0-9])')
        # split contractions right (both "'" and "’")
        self.numcs = re.compile(r"([0-9])'s")
        self.aca = re.compile(
            r"([a-zA-Z\u0080-\u024f])'([a-zA-Z\u0080-\u024f])")
        self.acna = re.compile(
            r"([a-zA-Z\u0080-\u024f])'([^a-zA-Z\u0080-\u024f])")
        self.nacna = re.compile(
            r"([^a-zA-Z\u0080-\u024f])'([^a-zA-Z\u0080-\u024f])")
        self.naca = re.compile(
            r"([^a-zA-Z0-9\u0080-\u024f])'([a-zA-Z\u0080-\u024f])")

        # split hyphens
        self.multihyphen = re.compile(r'(-+)')
        self.hypheninnun = re.compile(r'(-?[0-9]-+[0-9]-?){,}')
        self.ch_hyp_noalp = re.compile(r'(.)-([^a-zA-Z])')
        self.noalp_hyp_ch = re.compile(r'([^a-zA-Z])-(.)')
        # restore multi-dots
        self.restoredots = re.compile(r'(DOT)(\1*)MULTI')

        # split sentences
        if self.split_sen:
            self.splitsenr1 = re.compile(r' ([.?]) ([A-Z])')
            self.splitsenr2 = re.compile(r' ([.?]) ([\'"\(\{\[< ]+) ([A-Z])')
            self.splitsenr3 = re.compile(
                r' ([.?]) ([\'"\)\}\]> ]+) ([A-Z])')

    def normalize_punkt(self, text):
        """replace unicode punctuation by ascii"""
        text = re.sub('[\u2010\u2043]', '-', text)  # hyphen
        text = re.sub('[\u2018\u2019]', "'", text)  # single quotes
        text = re.sub('[\u201c\u201d]', '"', text)  # double quotes

        return text

    def tokenize(self, text):
        text = self.normalize_punkt(text)
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

        # split contractions right (both "'" and "’")
        text = self.nacna.sub(r"\1 ' \2", text)
        text = self.naca.sub(r"\1 ' \2", text)
        text = self.acna.sub(r"\1 ' \2", text)
        text = self.aca.sub(r"\1 '\2", text)
        text = self.numcs.sub(r"\1 's", text)

        text = text.replace("''", " ' ' ")
        # split dots at word beginings
        text = re.sub(r' (\.+)([^0-9])', r' \1 \2', text)

        # seperate out hyphens
        text = self.multihyphen.sub(
            lambda m: r'%s' % (' '.join(m.group(1))),
            text)
        text = self.hypheninnun.sub(
            lambda m: r'%s' % (m.group().replace('-', ' - ')),
            text)
        text = self.ch_hyp_noalp.sub(r'\1 - \2', text)
        text = self.noalp_hyp_ch.sub(r'\1 - \2', text)

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

        text = text.split()
        text = ' '.join(text)
        # restore multi-dots
        text = self.restoredots.sub(lambda m: r'.%s' %
                                    ('.' * int((len(m.group(2)) / 3))),
                                    text)

        # split sentences
        if self.split_sen:
            text = self.splitsenr1.sub(r' \1\n\2', text)
            text = self.splitsenr2.sub(r' \1\n\2 \3', text)
            text = self.splitsenr3.sub(r' \1 \2\n\3', text)

        return text

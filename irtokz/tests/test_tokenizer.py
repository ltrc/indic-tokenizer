#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from testtools import TestCase
from irtokz import tokenize_rom
from irtokz import tokenize_ind


class TestTokenizer(TestCase):

    def setUp(self):
        super(TestTokenizer, self).setUp()
        self.languages = "eng hin urd ben guj mal pan tel tam kan ori".split()
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def test_(self):
        for lang in self.languages:
            if lang == 'eng':
                tok = tokenize_rom(split_sen=True)
            else:
                tok = tokenize_ind(split_sen=True, lang=lang)
            with open('%s/%s.txt' % (self.test_dir, lang)) as fp:
                for line in fp:
                    tokenized_text = tok.tokenize(line)
                    self.assertIsInstance(tokenized_text, str)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys

from testtools import TestCase
from irtokz import RomanTokenizer
from irtokz import IndicTokenizer


class TestTokenizer(TestCase):

    def setUp(self):
        super(TestTokenizer, self).setUp()
        self.languages = "eng hin urd ben guj mal pan tel tam kan ori".split()
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def test_(self):
        for lang in self.languages:
            if lang == 'eng':
                tok = RomanTokenizer(split_sen=True)
            else:
                tok = IndicTokenizer(split_sen=True, lang=lang)
            with io.open('%s/%s.txt' % (self.test_dir, lang),
                         encoding='utf-8') as fp:
                for line in fp:
                    tokenized_text = tok.tokenize(line)
                    if sys.version_info[0] >= 3:
                        self.assertIsInstance(tokenized_text, str)
                    else:
                        self.assertIsInstance(tokenized_text, unicode)

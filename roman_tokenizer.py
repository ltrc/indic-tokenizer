#!/usr/bin/env python
# -*- coding=utf-8 -*-

import re
import os
import sys
import argparse

ENCHANT = True

try:
    import enchant
except ImportError:
    ENCHANT = False

class tokenizer():
    def __init__(self, split_sen=False):
	self.split_sen = split_sen
	file_path = os.path.abspath(__file__).rpartition('/')[0]
        if ENCHANT:
            self.en_dict = enchant.Dict('en_US')

        with open('%s/NONBREAKING_PREFIXES' %file_path) as fp:
            self.NBP = dict()
            for line in fp:
                if line.startswith('#'): continue
                if '#NUMERIC_ONLY#' in line:
                    self.NBP[line.replace('#NUMERIC_ONLY#', '').split()[0]] = 2
                else:
                    self.NBP[line.strip()] = 1

        #precompile regexes
        self.compile_regexes()

    def compile_regexes(self):
        # junk characters
        self.junk = re.compile('[\x00-\x1f]')
        # Latin-1 supplementary characters
        self.latin = re.compile(u'([\xa1-\xbf\xd7\xf7])')
        # general unicode punctituations except "’"
        self.upunct = re.compile(u'([\u2000-\u2018\u201a-\u206f])')
        # unicode mathematical operators
	self.umathop = re.compile(u'([\u2200-\u2211\u2213-\u22ff])')
        # unicode fractions
        self.ufrac = re.compile(u'([\u2150-\u2160])')
        # unicode superscripts and subscripts
        self.usupsub = re.compile(u'([\u2070-\u209f])')
        # unicode currency symbols
        self.ucurrency = re.compile(u'([\u20a0-\u20cf])')
        # all "other" ASCII special characters
        self.specascii = re.compile(u"([^\u0080-\U0010ffffa-zA-Z0-9\s\.',-])")

        #keep multiple dots together
        self.multidot = re.compile(r'(\.\.+)([^\.])')
        #seperate "," outside 
        self.notanumc = re.compile(r'([^0-9]),')
        self.cnotanum = re.compile(r',([^0-9])')
        #split contractions right (both "'" and "’")
        self.numcs = re.compile(u"([0-9])(['\u2019])s")
        self.aca = re.compile(u"([a-zA-Z\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])")
        self.acna = re.compile(u"([a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])")
        self.nacna = re.compile(u"([^a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])")
        self.naca = re.compile(u"([^a-zA-Z0-9\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])")

	#multiple hyphens
        self.multihyphen = re.compile('(-+)')
        self.hypheninnun = re.compile(r'(-?[0-9]-+[0-9]-?){,}')
        #restore multi-dots
        self.restoredots = re.compile(r'(DOT)(\1*)MULTI')

        #split sentences
        self.splitsenr1 = re.compile(u' ([!.?]) ([A-Z])')
        self.splitsenr2 = re.compile(u' ([!.?]) ([\u201c\u2018 ]+ [A-Z])')
        self.splitsenr3 = re.compile(u' ([!.?]) ([\'" ]+) ([A-Z])')
        self.splitsenr4 = re.compile(u' ([!.?]) ([\'"\)\}\]\u2019\u201d> ]+) ([A-Z])')

    def tokenize(self, text):
        text = ' %s ' %' '.join(text.split())
        # remove junk characters
        text = self.junk.sub('', text)
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
        # seperate out all "other" ASCII special characters
        text = self.specascii.sub(r' \1 ', text)        

        #keep multiple dots together
        text = self.multidot.sub(lambda m: r' %sMULTI %s' %('DOT'*len(m.group(1)), m.group(2)), text)
        #seperate "," outside 
        text = self.notanumc.sub(r'\1 , ', text)
        text = self.cnotanum.sub(r' , \1', text)
        #split contractions right (both "'" and "’")
        text = self.nacna.sub(r"\1 \2 \3", text)
        text = self.naca.sub(r"\1 \2 \3", text)
        text = self.acna.sub(r"\1 \2 \3", text)
        text = self.aca.sub(r"\1 \2\3", text)
        text = self.numcs.sub(r"\1 \2s", text)
        text = text.replace("''", " ' ' ")

        #handle non-breaking prefixes
        words = text.split()
        text_len = len(words) - 1 
        text = str()
        for i,word in enumerate(words):
            if word.endswith('.'):
                dotless = word[:-1]
                if dotless.isdigit(): 
                    word = dotless + ' .'
                elif ('.' in dotless and re.search('[a-zA-Z]', dotless)) or \
                    self.NBP.get(dotless, 0) == 1 or (i<text_len and words[i+1][0].islower()): pass 
                elif self.NBP.get(dotless, 0) == 2 and (i<text_len and words[i+1][0].isdigit()): pass
                elif i < text_len and words[i+1][0].isdigit():
                    if not ENCHANT: pass
                    elif ((len(dotless) > 2) and (self.en_dict.check(dotless.lower()) or \
                        self.en_dict.check(dotless.title()))):
                        word = dotless + ' .' 
                else: word = dotless + ' .'
            text += "%s " %word
      
	#seperate out hyphens
	text = self.multihyphen.sub(lambda m: r'%s' %(' '.join('-'*len(m.group(1)))), text) 
        text = self.hypheninnun.sub(lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        text = ' '.join(text.split())
        #restore multi-dots
        text = self.restoredots.sub(lambda m: r'.%s' %('.'*(len(m.group(2))/3)), text)

	#split sentences
	if self.split_sen:
	    text = self.splitsenr1.sub(r' \1\n\2', text)
            text = self.splitsenr2.sub(r' \1\n\2', text)
            text = self.splitsenr3.sub(r' \1\n\2 \3', text)
	    text = self.splitsenr4.sub(r' \1 \2\n\3', text)
        
        return text

if __name__ == '__main__':
    
    # parse command line arguments 
    parser = argparse.ArgumentParser(prog="roman_tokenizer", description="Tokenizer for Roman-Scripts")
    parser.add_argument('--i', metavar='input', dest="INFILE", type=argparse.FileType('r'), default=sys.stdin, help="<input-file>")
    parser.add_argument('--s', dest='split_sen', action='store_true', help="set this flag for splittting on sentence boundaries")
    parser.add_argument('--o', metavar='output', dest="OUTFILE", type=argparse.FileType('w'), default=sys.stdout, help="<output-file>")
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenizer(split_sen=args.split_sen)
    # convert data
    for line in args.INFILE:
        line = line.decode('utf-8')
        line = tzr.tokenize(line)
        line = line.encode('utf-8')
        args.OUTFILE.write('%s\n' %line)

    # close files 
    args.INFILE.close()
    args.OUTFILE.close()


    
        

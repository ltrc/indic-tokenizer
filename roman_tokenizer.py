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
    def __init__(self):
	file_path = os.path.abspath(__file__).rpartition('/')[0]
        if ENCHANT:
            self.en_dict = enchant.Dict('en_US')

        with open('%s/NONBREAKING_PREFIXES' %file_path) as fp:
            self.NBP = dict()
            for line in fp:
                if not line.startswith('#'):
                    if '#NUMERIC_ONLY#' in line:
                        self.NBP[line.replace('#NUMERIC_ONLY#', '').split()[0]] = 2
                    else:
                        self.NBP[line.strip()] = 1

    def tokenize(self, text):
        text = ' %s ' %' '.join(text.split())
        # remove junk characters
        text = re.sub('[\x00-\x1f]', '', text)
        # seperate out on Latin-1 supplementary characters
        text = re.sub(u'([\xa1-\xbf\xd7\xf7])', r' \1 ', text)        
        # seperate out on general unicode punctituations except "’"
        text = re.sub(u'([\u2000-\u2018\u201a-\u206f])', r' \1 ', text)        
        # seperate out on unicode mathematical operators
        text = re.sub(u'([\u2200-\u22ff])', r' \1 ', text)        
        # seperate out on unicode fractions
        text = re.sub(u'([\u2150-\u2160])', r' \1 ', text)        
        # seperate out on unicode superscripts and subscripts
        text = re.sub(u'([\u2070-\u209f])', r' \1 ', text)        
        # seperate out on unicode currency symbols
        text = re.sub(u'([\u20a0-\u20cf])', r' \1 ', text)        
        # seperate out all "other" special characters
        text = re.sub(u"([^\u0080-\U0010ffffa-zA-Z0-9\s\.'`,-])", r' \1 ', text)        

        #keep multiple dots together
        text = re.sub(r'(\.\.+)([^\.])', lambda m: r' %sMULTI %s' %('DOT'*len(m.group(1)), m.group(2)), text)
        #seperate "," outside 
        text = re.sub(r'([^0-9]),', r'\1 , ', text)
        text = re.sub(r',([^0-9])', r' , \1', text)
        #split contractions right (both "'" and "’")
        text = re.sub(u"([^a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])", r"\1 \2 \3", text)
        text = re.sub(u"([^a-zA-Z0-9\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])", r"\1 \2 \3", text)
        text = re.sub(u"([a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])", r"\1 \2 \3", text)
        text = re.sub(u"([a-zA-Z\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])", r"\1 \2\3", text)
        text = re.sub(u"([0-9])(['\u2019])s", r"\1 \2s", text)
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
      
	text = re.sub('(-+)', lambda m: r'%s' %(' '.join('-'*len(m.group(1)))), text) 
        text = re.sub(r'(-?[0-9]-+[0-9]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        text = ' '.join(text.split())
        #restore multi-dots
        text = re.sub(r'(DOT)(\1*)MULTI', lambda m: r'.%s' %('.'*(len(m.group(2))/3)), text)

	#split sentences
        text = re.sub(u' ([!.?]) ([a-zA-Z])', r' \1\n\2', text)
	text = re.sub(u' ([!.?]) ([\)\}\]\'"\u2019\u201d>]) ', r' \1 \2\n', text)
        #text = re.sub(u' ([!.?]) ([^a-zA-Z]) ', r' \1 \2\n', text)
        
        return text

if __name__ == '__main__':
    
    # parse command line arguments 
    parser = argparse.ArgumentParser(prog="roman_tokenizer", description="Tokenizer for Roman-Scripts")
    parser.add_argument('--i', metavar='input', dest="INFILE", type=argparse.FileType('r'), default=sys.stdin, help="<input-file>")
    parser.add_argument('--o', metavar='output', dest="OUTFILE", type=argparse.FileType('w'), default=sys.stdout, help="<output-file>")
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenizer()
    # convert data
    for line in args.INFILE:
        line = line.decode('utf-8')
        line = tzr.tokenize(line)
        line = line.encode('utf-8')
        args.OUTFILE.write('%s\n' %line)

    # close files 
    args.INFILE.close()
    args.OUTFILE.close()


    
        

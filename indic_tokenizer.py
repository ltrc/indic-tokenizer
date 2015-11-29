#!/usr/bin/env python
# -*- coding=utf-8 -*-

import re
import sys
import os.path
import argparse

ENCHANT = True

try:
    import enchant
except ImportError:
    ENCHANT = False

class tokenizer():
    def __init__(self, lang='hin', split_sen=False):
        self.lang = lang
	self.split_sen = split_sen
        self.WORD_JOINER=u'\u2060'
        self.SOFT_HYPHEN=u'\u00AD'
        self.BYTE_ORDER_MARK=u'\uFEFF'
        self.BYTE_ORDER_MARK_2=u'\uFFFE'
        self.NO_BREAK_SPACE=u'\u00A0'
        self.ZERO_WIDTH_SPACE=u'\u200B'
        self.ZERO_WIDTH_JOINER=u'\u200D'
        self.ZERO_WIDTH_NON_JOINER=u'\u200C'

        file_path = os.path.abspath(__file__).rpartition('/')[0]
        if ENCHANT:
            self.en_dict = enchant.Dict('en_US')

        self.ben = lang in ["ben", "asm"]
        self.dev = lang in ["hin", "mar", "nep", "bod", "kok"]
	self.urd = lang == 'urd'
	self.tam = lang == 'tam'
	self.tel = lang == 'tel'
	self.mal = lang == 'mal'
	self.kan = lang == 'kan'
	self.guj = lang == 'guj'
	self.pan = lang == 'pan'
	self.ori = lang == 'ori'

        #load nonbreaking prefixes from file
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
        # remove junk characters
        self.junk = re.compile('[\x00-\x1f]')
        # seperate out on Latin-1 supplementary characters
        self.latin = re.compile(u'([\xa1-\xbf\xd7\xf7])')
        # seperate out on general unicode punctituations except "’"
        self.upunct = re.compile(u'([\u2000-\u2018\u201a-\u206f])')
        # seperate out on unicode mathematical operators
        self.umathop = re.compile(u'([\u2200-\u2211\u2213-\u22ff])')
        # seperate out on unicode fractions
        self.ufrac = re.compile(u'([\u2150-\u2160])')
        # seperate out on unicode superscripts and subscripts
        self.usupsub = re.compile(u'([\u2070-\u209f])')
        # seperate out on unicode currency symbols
        self.ucurrency = re.compile(u'([\u20a0-\u20cf])')
        # seperate out all "other" ASCII special characters
        self.specascii = re.compile(u"([^\u0080-\U0010ffffa-zA-Z0-9\s\.'`,-])")	

        #keep multiple dots together
        self.multidot = re.compile(r'(\.\.+)([^\.])')
        if self.urd:
            #keep multiple dots (urdu-dots) together
            self.multidot_urd = re.compile(u'(\u06d4\u06d4+)([^\u06d4])')
        else:
            #keep multiple purna-viram together
            self.multiviram = re.compile(u'(\u0964\u0964+)([^\u0964])')
            #keep multiple purna deergh-viram together
            self.multidviram = re.compile(u'(\u0965\u0965+)([^\u0965])')
        #split contractions right (both "'" and "’")
        self.numcs = re.compile(u"([0-9\u0966-\u096f])(['\u2019])s")
        self.aca = re.compile(u"([a-zA-Z\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])")
        self.acna = re.compile(u"([a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])")
        self.nacna = re.compile(u"([^a-zA-Z\u0080-\u024f])(['\u2019])([^a-zA-Z\u0080-\u024f])")
        self.naca = re.compile(u"([^a-zA-Z0-9\u0966-\u096f\u0080-\u024f])(['\u2019])([a-zA-Z\u0080-\u024f])")

        #multiple hyphens
        self.multihyphen = re.compile('(-+)')
        #restore multi-dots
        self.restoredots = re.compile(r'(DOT)(\1*)MULTI')
        if self.urd:
            self.restoreudots = re.compile(r'(DOTU)(\1*)MULTI')
        else:
            self.restoreviram = re.compile(r'(PNVM)(\1*)MULTI')
            self.restoredviram = re.compile(r'(DGVM)(\1*)MULTI')

        #split sentences
        if self.urd:
            self.splitsenur1 = re.compile(u' ([!.?\u06d4]) ([\u0617-\u061a\u0620-\u065f\u066e-\u06d3\u06d5\u06fa-\u06ff\u201d\u2019A-Z])')
            self.splitsenur2 = re.compile(u' ([!.?\u06d4]) ([\)\}\]\'"\u2018\u201c> ]+) ')
        else: 
            self.splitsenir1 = re.compile(u' ([!.?\u0964\u0965]) ([\u0900-\u0d7f\u201c\u2018A-Z])')
            self.splitsenir2 = re.compile(u' ([!.?\u0964\u0965]) ([\)\}\]\'"\u2019\u201d> ]+) ')

    def normalize(self,text):
        """
        Performs some common normalization, which includes: 
            - Byte order mark, word joiner, etc. removal 
            - ZERO_WIDTH_NON_JOINER and ZERO_WIDTH_JOINER removal 
            - ZERO_WIDTH_SPACE and NO_BREAK_SPACE replaced by spaces 
        """

        text=text.replace(self.BYTE_ORDER_MARK,'')
        text=text.replace(self.BYTE_ORDER_MARK_2,'')
        text=text.replace(self.WORD_JOINER,'')
        text=text.replace(self.SOFT_HYPHEN,'')

        text=text.replace(self.ZERO_WIDTH_SPACE,' ') 
        text=text.replace(self.NO_BREAK_SPACE,' ')

        text=text.replace(self.ZERO_WIDTH_NON_JOINER, '')
        text=text.replace(self.ZERO_WIDTH_JOINER,'')

        return text

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
	if self.urd:
	    #keep multiple dots (urdu-dots) together
	    text = self.multidot_urd.sub(lambda m: r' %sMULTI %s' %('DOTU'*len(m.group(1)), m.group(2)), text)
	else:
	    #keep multiple purna-viram together
	    text = self.multiviram.sub(lambda m: r' %sMULTI %s' %('PNVM'*len(m.group(1)), m.group(2)), text)
	    #keep multiple purna deergh-viram together
	    text = self.multidviram.sub(lambda m: r' %sMULTI %s' %('DGVM'*len(m.group(1)), m.group(2)), text)

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

        if self.dev:
            #seperate out "," except for Hindi and Ascii digits
            text = re.sub(u'([^0-9\u0966-\u096f]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0966-\u096f])', r' , \1', text)
            #separate out on Hindi characters followed by non-Hindi characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0900-\u0965\u0970-\u097f])([^\u0900-\u0965\u0970-\u097f\u2212-]|[\u0964\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0900-\u0965\u0970-\u097f\u2212-]|[\u0964\u0965])([\u0900-\u0965\u0970-\u097f])', r'\1 \2', text)
        elif self.ben:
            #seperate out "," except for Bengali and Ascii digits
            text = re.sub(u'([^0-9\u09e6-\u09ef]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u09e6-\u09ef])', r' , \1', text)
            #separate out on Bengali characters followed by non-Bengali characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0980-\u09e5\u09f0-\u09ff])([^\u0980-\u09e5\u09f0-\u09ff\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0980-\u09e5\u09f0-\u09ff\u2212-]|[\u0964-\u0965])([\u0980-\u09e5\u09f0-\u09ff])', r'\1 \2', text)
            #seperate out Bengali special chars (currency signs, BENGALI ISSHAR)
            text = re.sub(u'([\u09f2\u09f3\u09fa\u09fb])', r' \1 ', text)
        elif self.guj:
            #seperate out "," except for Gujrati and Ascii digits
            text = re.sub(u'([^0-9\u0ae6-\u0aef]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0ae6-\u0aef])', r' , \1', text)
            #separate out on Gujrati characters followed by non-Gujrati characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0A80-\u0AE5\u0Af0-\u0Aff])([^\u0A80-\u0AE5\u0Af0-\u0Aff\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0A80-\u0AE5\u0Af0-\u0Aff\u2212-]|[\u0964-\u0965])([\u0A80-\u0AE5\u0Af0-\u0Aff])', r'\1 \2', text)
            #seperate out Gujurati special chars (currency signs, GUJARATI OM)
            text = re.sub(u'([\u0AD0\u0AF1])', r' \1 ', text)
        elif self.mal:
            #seperate out "," except for Malayalam and Ascii digits
            text = re.sub(u'([^0-9\u0d66-\u0d6f]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0d66-\u0d6f])', r' , \1', text)
            #separate out on Malayalam characters followed by non-Malayalam characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0D00-\u0D65\u0D73-\u0D7f])([^\u0D00-\u0D65\u0D73-\u0D7f\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0D00-\u0D65\u0D73-\u0D7f\u2212-]|[\u0964-\u0965])([\u0D00-\u0D65\u0D73-\u0D7f])', r'\1 \2', text)
            #seperate out Malayalam fraction symbols
            text = re.sub(u'([\u0d73\u0d74\u0d75])', r' \1 ', text)
        elif self.pan:
            #seperate out "," except for Punjabi and Ascii digits
            text = re.sub(u'([^0-9\u0a66-\u0a6f]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0a66-\u0a6f])', r' , \1', text)
            #separate out on Punjabi characters followed by non-Punjabi characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0A00-\u0A65\u0A70-\u0A7f])([^\u0A00-\u0A65\u0A70-\u0A7f\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0A00-\u0A65\u0A70-\u0A7f\u2212-]|[\u0964-\u0965])([\u0A00-\u0A65\u0A70-\u0A7f])', r'\1 \2', text)
        elif self.tel:
            #seperate out "," except for Telugu and Ascii digits
            text = re.sub(u'([^0-9\u0c66-\u0c6f]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0c66-\u0c6f])', r' , \1', text)
            #separate out on Telugu characters followed by non-Telugu characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0c00-\u0c65\u0c70-\u0c7f])([^\u0c00-\u0c65\u0c70-\u0c7f\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0c00-\u0c65\u0c70-\u0c7f\u2212-]|[\u0964-\u0965])([\u0c00-\u0c65\u0c70-\u0c7f])', r'\1 \2', text)
            #separate out Telugu fractions and weights
            text = re.sub(u'([\u0c78-\u0c7f])', r' \1 ', text)
        elif self.tam:
            #seperate out "," except for Tamil and Ascii digits
            text = re.sub(u'([^0-9\u0be6-\u0bef]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0be6-\u0bef])', r' , \1', text)
            #separate out on Tamil characters followed by non-Tamil characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0B80-\u0Be5\u0Bf3-\u0Bff])([^\u0B80-\u0Be5\u0Bf3-\u0Bff\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0B80-\u0Be5\u0Bf3-\u0Bff\u2212-]|[\u0964-\u0965])([\u0B80-\u0Be5\u0Bf3-\u0Bff])', r'\1 \2', text)
            #seperate out Tamil special symbols (calendrical, clerical, currency signs etc.)
            text = re.sub(u'([\u0bd0\u0bf3-\u0bff])', r' \1 ', text)
        elif self.kan:
            #seperate out "," except for Kanadda and Ascii digits
            text = re.sub(u'([^0-9\u0ce6-\u0cef]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0ce6-\u0cef])', r' , \1', text)
            #separate out on Kanadda characters followed by non-Kanadda characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0C80-\u0Ce5\u0Cf1-\u0Cff])([^\u0C80-\u0Ce5\u0Cf1-\u0Cff\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0C80-\u0Ce5\u0Cf1-\u0Cff]\u2212-|[\u0964-\u0965])([\u0C80-\u0Ce5\u0Cf1-\u0Cff])', r'\1 \2', text)
        elif self.ori:
            #seperate out "," except for Oriya and Ascii digits
            text = re.sub(u'([^0-9\u0b66-\u0b6f]),', r'\1 , ', text)
            text = re.sub(u',([^0-9\u0b66-\u0b6f])', r' , \1', text)
            #separate out on Oriya characters followed by non-Oriya characters or purna viram or deergh viram and vice-versa
            text = re.sub(u'([\u0B00-\u0B65\u0B70-\u0B7f])([^\u0B00-\u0B65\u0B70-\u0B7f\u2212-]|[\u0964-\u0965])', r'\1 \2', text)
            text = re.sub(u'([^\u0B00-\u0B65\u0B70-\u0B7f\u2212-]|[\u0964-\u0965])([\u0B00-\u0B65\u0B70-\u0B7f])', r'\1 \2', text)
            #seperate out Oriya fraction symbols
            text = re.sub(u'([\u0B72-\u0B77])', r' \1 ', text)
        elif self.urd:
            #seperate out urdu full-stop i.e., "۔"
            text = text.replace(u'\u06d4', u' \u06d4 ')
            #seperate out urdu quotation marks i.e., "٬"
            text = text.replace(u'\u066c', u' \u066c ')
            #seperate out Urdu comma i.e., "،" except for Urdu digits
            text = re.sub(u'([^\u0660-\u0669\u06f0-\u06f9])\u060C', ur'\1 \u060C ', text)
            text = re.sub(u'\u060C([^\u0660-\u0669\u06f0-\u06f9])', ur' \u060C \1', text)
            #separate out on Urdu characters followed by non-Urdu characters and vice-versa
            text = re.sub(u'([\u0617-\u061a\u0620-\u065f\u066e-\u06d3\u06d5\u06fa-\u06ff\ufe70-\ufeff])' +
                            u'([^\u0617-\u061a\u0620-\u065f\u066e-\u06d3\u06d5\u06fa-\u06ff\ufe70-\ufeff\u2212-])', r'\1 \2', text)
            text = re.sub(u'([^\u0617-\u061a\u0620-\u065f\u066e-\u06d3\u06d5\u06fa-\u06ff\ufe70-\ufeff\u2212-])' +
                            u'([\u0617-\u061a\u0620-\u065f\u066e-\u06d3\u06d5\u06fa-\u06ff\ufe70-\ufeff])', r'\1 \2', text)
            #separate out on every other special character
            text = re.sub(u'([\u0600-\u0607\u0609\u060a\u060d\u060e\u0610-\u0614\u061b-\u061f\u066a-\u066d\u06dd\u06de\u06e9])',
                            r' \1 ', text)

	if not self.urd:
	    #Normalize "|" to purna viram 
	    text = text.replace('|', u'\u0964')
	    #Normalize ". ।" to "।"
	    text = re.sub(u'\.\s+\u0964', u'\u0964', text)
      
	#seperate out hyphens 
        text = self.multihyphen.sub(lambda m: r'%s' %(' '.join('-'*len(m.group(1)))), text) 
	if self.dev:
            text = re.sub(u'(-?[0-9\u0966-\u096f]-+[0-9\u0966-\u096f]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.ben:
            text = re.sub(u'(-?[0-9\u09e6-\u09ef]-+[0-9\u09e6-\u09ef]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.guj:
            text = re.sub(u'(-?[0-9\u0ae6-\u0aef]-+[0-9\u0ae6-\u0aef]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.mal:
            text = re.sub(u'(-?[0-9\u0d66-\u0D72]-+[0-9\u0d66-\u0D72]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.pan:
            text = re.sub(u'(-?[0-9\u0a66-\u0a6f]-+[0-9\u0a66-\u0a6f]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.tel:
            text = re.sub(u'(-?[0-9\u0c66-\u0c6f]-+[0-9\u0c66-\u0c6f]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.tam:
            text = re.sub(u'(-?[0-9\u0be6-\u0bf2]-+[0-9\u0be6-\u0bf2]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.kan:
            text = re.sub(u'(-?[0-9\u0ce6-\u0cef]-+[0-9\u0ce6-\u0cef]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.ori:
            text = re.sub(u'(-?[0-9\u0b66-\u0b6f]-+[0-9\u0b66-\u0b6f]-?){,}',lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        elif self.urd:
            text = re.sub(u'(-?[0-9\u0660-\u0669\u06f0-\u06f9]-+[0-9\u0660-\u0669\u06f0-\u06f9]-?){,}',
                            lambda m: r'%s' %(m.group().replace('-', ' - ')), text)
        text = ' '.join(text.split())

        #restore multiple dots, purna virams and deergh virams
        text = self.restoredots.sub(lambda m: r'.%s' %('.'*(len(m.group(2))/3)), text)
	if self.urd:
	    text = self.restoreudots.sub(lambda m: u'\u06d4%s' %(u'\u06d4'*(len(m.group(2))/3)), text)
	else:
	    text = self.restoreviram.sub(lambda m: u'\u0964%s' %(u'\u0964'*(len(m.group(2))/4)), text)
	    text = self.restoredviram.sub(lambda m: u'\u0965%s' %(u'\u0965'*(len(m.group(2))/4)), text)

	#split sentences
	if self.split_sen:
	    if self.urd: 
	        text = self.splitsenur1.sub(r' \1\n\2', text)
	        text = self.splitsenur2.sub(r' \1 \2\n', text)
	    else: 
	        text = self.splitsenir1.sub(r' \1\n\2', text)
	        text = self.splitsenir2.sub(r' \1 \2\n', text)

        return text

if __name__ == '__main__':
    
    lang_help = """select language (3 letter ISO-639 code)
		Hindi       : hin
		Urdu	    : urd
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
		Assamese    : asm"""
    languages = "hin urd ben asm guj mal pan tel tam kan ori mar nep bod kok".split()
    # parse command line arguments 
    parser = argparse.ArgumentParser(prog="indic_tokenizer", 
                                    description="Tokenizer for Indian Scripts",
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--i', metavar='input', dest="INFILE", type=argparse.FileType('r'), default=sys.stdin, help="<input-file>")
    parser.add_argument('--l', metavar='language', dest="lang", choices=languages, default='hin', help=lang_help)
    parser.add_argument('--s', dest='split_sen', action='store_true', help="set this flag for splittting on sentence boundaries")
    parser.add_argument('--o', metavar='output', dest="OUTFILE", type=argparse.FileType('w'), default=sys.stdout, help="<output-file>")
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenizer(lang=args.lang, split_sen=args.split_sen)
    # convert data
    for line in args.INFILE:
        line = line.decode('utf-8')
        line = tzr.normalize(line)
        line = tzr.tokenize(line)
        line = line.encode('utf-8')
        args.OUTFILE.write('%s\n' %line)

    # close files 
    args.INFILE.close()
    args.OUTFILE.close()

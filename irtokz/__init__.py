#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tokenizer for Indian scripts and Roman script.

This module provides a complete tokenizer for Indian languages
including Urdu, Kashmiri and Roman script.

Copyright (c) 2015-2016 Irshad Ahmad
<irshad.bhat@research.iiit.ac.in>

Distributed under MIT license
[http://opensource.org/licenses/mit-license.html].
"""

from __future__ import print_function

import io
import sys
import codecs
import socket
import argparse
import threading
import multiprocessing

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .indic_tokenize import IndicTokenizer
from .roman_tokenize import RomanTokenizer

__name__ = 'Indic Tokenizer'
__author__ = 'Irshad Ahmad'
__copyright__ = 'Copyright (C) 2015-16 Irshad Ahmad'
__version__ = '1.0.3'
__license__ = 'MIT'
__maintainer__ = 'Irshad Ahmad'
__email__ = 'irshad.bhat@research.iiit.ac.in'
__status__ = 'Beta'
__all__ = ['indic_tokenize', 'roman_tokenize']

_MAX_BUFFER_SIZE_ = 1024000  # 1MB


def processInput(inFD, outFD, tok):
    # convert data
    for line in inFD:
        line = tok.tokenize(line)
        outFD.write('%s\n' % line)


class ClientThread(threading.Thread):
    def __init__(self, ip, port, clientsocket, tok):
        threading.Thread.__init__(self)
        self.tok = tok
        self.ip = ip
        self.port = port
        self.csocket = clientsocket
        # print('[+] New thread started for '+ip+':'+str(port))

    def run(self):
        # print('Connection from : '+ip+':'+str(port))
        data = self.csocket.recv(_MAX_BUFFER_SIZE_)
        # print('Client(%s:%s) sent : %s'%(self.ip, str(self.port), data))
        fakeInputFile = StringIO.StringIO(data)
        fakeOutputFile = StringIO.StringIO('')
        processInput(fakeInputFile, fakeOutputFile, self.tok)
        fakeInputFile.close()
        self.csocket.send(fakeOutputFile.getvalue())
        fakeOutputFile.close()
        self.csocket.close()

        # print('Client at '+self.ip+' disconnected...')


def parse_args(args, indic=True):
    if indic:
        prog = 'Indic-Tokenizer'
        description = 'Tokenizer for Indian Scripts'
        languages = '''hin urd ben asm guj mal pan tel tam kan ori mar
                    nep bod kok kas'''.split()
        lang_help = 'select language (3 letter ISO-639 code) {%s}' % (
                    ', '.join(languages))
    else:
        prog = 'Roman-Tokenizer'
        description = 'Tokenizer for Roman Script'
    # parse command line arguments
    parser = argparse.ArgumentParser(prog=prog,
                                     description=description)
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='%s %s' % (prog, __version__))
    parser.add_argument('-i',
                        '--input',
                        metavar='',
                        dest='infile',
                        type=str,
                        help='<input-file>')
    parser.add_argument('-s',
                        '--split-sentences',
                        dest='split_sen',
                        action='store_true',
                        help='set this flag to apply'
                             ' sentence segmentation')
    parser.add_argument('-o',
                        '--output',
                        metavar='',
                        dest='outfile',
                        type=str,
                        help='<output-file>')
    parser.add_argument('-d',
                        '--daemonize',
                        dest='isDaemon',
                        help='Do you want to daemonize me?',
                        action='store_true',
                        default=False)
    parser.add_argument('-p',
                        '--port',
                        metavar='',
                        type=int,
                        dest='daemonPort',
                        help='Specify a port number')
    if indic:
        parser.add_argument('-l',
                            '--language',
                            metavar='',
                            dest='lang',
                            choices=languages,
                            default='hin',
                            help=lang_help)
    args = parser.parse_args(args)
    return args


def ind_main():
    # parse arguments
    args = parse_args(sys.argv[1:])

    if args.infile:
        ifp = io.open(args.infile, encoding='utf-8')
    else:
        if sys.version_info[0] >= 3:
            ifp = codecs.getreader('utf8')(sys.stdin.buffer)
        else:
            ifp = codecs.getreader('utf8')(sys.stdin)

    if args.outfile:
        ofp = io.open(args.outfile, mode='w', encoding='utf-8')
    else:
        if sys.version_info[0] >= 3:
            ofp = codecs.getwriter('utf8')(sys.stdout.buffer)
        else:
            ofp = codecs.getwriter('utf8')(sys.stdout)

    # initialize convertor object
    tok = IndicTokenizer(lang=args.lang, split_sen=args.split_sen)

    # convert data
    if args.isDaemon and args.daemonPort:
        host = '0.0.0.0'  # Listen on all interfaces
        port = args.daemonPort  # Port number

        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        tcpsock.bind((host, port))

        while True:
            tcpsock.listen(multiprocessing.cpu_count())
            # print('nListening for incoming connections...')
            (clientsock, (ip, port)) = tcpsock.accept()

            # pass clientsock to the ClientThread thread object being created
            newthread = ClientThread(ip, port, clientsock, tok)
            newthread.start()
    else:
        processInput(ifp, ofp, tok)

    # close files
    ifp.close()
    ofp.close()


def rom_main():
    # parse arguments
    args = parse_args(sys.argv[1:], indic=False)

    if args.infile:
        ifp = io.open(args.infile, encoding='utf-8')
    else:
        if sys.version_info[0] >= 3:
            ifp = codecs.getreader('utf8')(sys.stdin.buffer)
        else:
            ifp = codecs.getreader('utf8')(sys.stdin)

    if args.outfile:
        ofp = io.open(args.outfile, mode='w', encoding='utf-8')
    else:
        if sys.version_info[0] >= 3:
            ofp = codecs.getwriter('utf8')(sys.stdout.buffer)
        else:
            ofp = codecs.getwriter('utf8')(sys.stdout)

    # initialize convertor object
    tok = RomanTokenizer(split_sen=args.split_sen)

    # convert data
    if args.isDaemon and args.daemonPort:
        host = '0.0.0.0'  # Listen on all interfaces
        port = args.daemonPort  # Port number

        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        tcpsock.bind((host, port))

        while True:
            tcpsock.listen(multiprocessing.cpu_count())
            # print('nListening for incoming connections...')
            (clientsock, (ip, port)) = tcpsock.accept()

            # pass clientsock to the ClientThread thread object being created
            newthread = ClientThread(ip, port, clientsock, tok)
            newthread.start()
    else:
        processInput(ifp, ofp, tok)

    # close files
    ifp.close()
    ofp.close()

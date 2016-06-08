#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tokenizer for Indian scripts and Roman script.

This module provides a complete tokenizer for Indian languages
including Urdu and Kashmiri and Roman script.

Copyright (c) 2015-2016 Irshad Ahmad
<irshad.bhat@research.iiit.ac.in>

Distributed under MIT license
[http://opensource.org/licenses/mit-license.html].
"""

from __future__ import print_function

import sys
import socket
import argparse
import StringIO
import threading
import multiprocessing

from .indic_tokenize import tokenize_ind
from .roman_tokenize import tokenize_rom

__name__ = "Indic Tokenizer"
__author__ = "Irshad Ahmad"
__copyright__ = "Copyright (C) 2015-16 Irshad Ahmad"
__version__ = "1.0"
__license__ = "MIT"
__maintainer__ = "Irshad Ahmad"
__email__ = "irshad.bhat@research.iiit.ac.in"
__status__ = "Beta"
__all__ = ["indic_tokenize", "roman_tokenize"]

_MAX_BUFFER_SIZE_ = 1024000  # 1MB


def processInput(inFD, outFD, tzr):
    # convert data
    for line in inFD:
        line = tzr.tokenize(line)
        outFD.write('%s\n' % line)


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket, tzr):
        threading.Thread.__init__(self)
        self.tzr = tzr
        self.ip = ip
        self.port = port
        self.csocket = clientsocket
        # print "[+] New thread started for "+ip+":"+str(port)

    def run(self):
        # print "Connection from : "+ip+":"+str(port)
        data = self.csocket.recv(_MAX_BUFFER_SIZE_)
        # print "Client(%s:%s) sent : %s"%(self.ip, str(self.port), data)
        fakeInputFile = StringIO.StringIO(data)
        fakeOutputFile = StringIO.StringIO("")
        processInput(fakeInputFile, fakeOutputFile, self.tzr)
        fakeInputFile.close()
        self.csocket.send(fakeOutputFile.getvalue())
        fakeOutputFile.close()
        self.csocket.close()

        # print "Client at "+self.ip+" disconnected..."


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
    languages = "hin urd ben asm guj mal pan tel tam \
        kan ori mar nep bod kok kas".split()
    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog="indic_tokenizer",
        description="Tokenizer for Indian Scripts",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--i',
        metavar='input',
        dest="INFILE",
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="<input-file>")
    parser.add_argument(
        '--l',
        metavar='language',
        dest="lang",
        choices=languages,
        default='hin',
        help=lang_help)
    parser.add_argument(
        '--s',
        dest='split_sen',
        action='store_true',
        help="set this flag to apply sentence segmentation")
    parser.add_argument(
        '--o',
        metavar='output',
        dest="OUTFILE",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="<output-file>")
    parser.add_argument(
        '--daemonize',
        dest='isDaemon',
        help='Do you want to daemonize me?',
        action='store_true',
        default=False)
    parser.add_argument(
        '--port',
        type=int,
        dest='daemonPort',
        help='Specify a port number')
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenize_ind(lang=args.lang, split_sen=args.split_sen)

    # convert data
    if args.isDaemon and args.daemonPort:
        host = "0.0.0.0"  # Listen on all interfaces
        port = args.daemonPort  # Port number

        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        tcpsock.bind((host, port))

        while True:
            tcpsock.listen(multiprocessing.cpu_count())
            # print "nListening for incoming connections..."
            (clientsock, (ip, port)) = tcpsock.accept()

            # pass clientsock to the ClientThread thread object being created
            newthread = ClientThread(ip, port, clientsock, tzr)
            newthread.start()
    else:
        processInput(args.INFILE, args.OUTFILE, tzr)

    # close files
    args.INFILE.close()
    args.OUTFILE.close()


def rom_main():
    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog="roman_tokenizer",
        description="Tokenizer for Roman-Script")
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
        help="set this flag to apply sentence segmentation")
    parser.add_argument(
        '--o',
        metavar='output',
        dest="OUTFILE",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="<output-file>")
    parser.add_argument(
        '--daemonize',
        dest='isDaemon',
        help='Do you want to daemonize me?',
        action='store_true',
        default=False)
    parser.add_argument(
        '--port',
        type=int,
        dest='daemonPort',
        help='Specify a port number')
    args = parser.parse_args()

    # initialize convertor object
    tzr = tokenize_rom(split_sen=args.split_sen)

    # convert data
    if args.isDaemon and args.daemonPort:
        host = "0.0.0.0"  # Listen on all interfaces
        port = args.daemonPort  # Port number

        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        tcpsock.bind((host, port))

        while True:
            tcpsock.listen(multiprocessing.cpu_count())
            # print "nListening for incoming connections..."
            (clientsock, (ip, port)) = tcpsock.accept()

            # pass clientsock to the ClientThread thread object being created
            newthread = ClientThread(ip, port, clientsock, tzr)
            newthread.start()
    else:
        processInput(args.INFILE, args.OUTFILE, tzr)

    # close files
    args.INFILE.close()
    args.OUTFILE.close()

if __name__ == '__main__':
    rom_main()
    # ind_main()

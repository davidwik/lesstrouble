#!/usr/bin/python
# -*- coding: utf-8 -*-
import optparse
import sys
import os
import subprocess
import time
import termios
import re


def parse_args():
    usage = (
        "%prog [options] [input file] [output file]"
        "lesstrouble.py is a very simple LESS monitor."
        "It generates CSS via your installed version of the lessc compiler."
        "This utility checks for changes on 'input file' and its dependencies."
        "If a change is noticed it calls the LESS compiler and "
        "generates an output file."
        ""
        ""
        "> lesstrouble.py [options] inputfile.less [outputfile.css]")
    parser = optparse.OptionParser(usage)
    parser.add_option('-c',
                      '--compress',
                      action='store_true',
                      dest='compress',
                      help='Compress the generated CSS file')
    args = parser.parse_args()
    devnull = open(os.devnull, 'w')

    try:
        subprocess.call('lessc', stdout=devnull)
    except OSError:
        print ("\n%sThe LESS compiler doesn't seem to be installed."
               "Please install it via 'npm less'\n") % (TermColors.FAIL)
        sys.exit(1)

    if len(args[1]) < 1:
        print "\n%sError: You need to specify one LESS file.\n" % (
            TermColors.FAIL
        )
        sys.exit(1)

    if '.less' not in args[1][0]:
        print "\n%sError: The input file must be a LESS file.\n" % (
            TermColors.FAIL
        )
        sys.exit(1)

    if not os.path.isfile(os.getcwd() + os.sep + args[1][0]):
        print "\n%sError: Input file %s doesn't exists!\n" % (
            TermColors.FAIL,
            args[1][0]
            )
        sys.exit(1)

    if len(args[1]) > 1:
        if args[1][1].endswith('.css') is False:
            print "\n%sError: The output file must be a CSS file.\n" % (
                TermColors.FAIL
            )
            sys.exit(1)

    if len(args[1]) > 1:
        of = os.path.abspath(args[1][1])
        od = os.sep.join(of.split(os.sep)[:-1])

        if not os.path.isdir(od):
            print ("\n%sThe output directory: %s\nDoes not exist, "
                   "please create the directory first.\n") % (
                       TermColors.FAIL,
                       od
            )
            sys.exit(1)
    return args


class TermColors:
    DEFAULT = '\033[37m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'


class LessListener:
    anim = [
        '(*---------)', '(-*--------)', '(--*-------)',
        '(---*------)',  '(----*-----)',  '(-----*----)',
        '(------*---)',  '(-------*--)',  '(--------*-)',
        '(---------*)'
    ]

    def startup(self):
        header = """%s%s######################################################
|                                                    |
|           %sAUTOMATIC LESS GENERATOR v0.1%s            |
|                                                    |
| This script reads a LESS file and keeps monitoring |
|    all the dependencies for a project. A lessc     |
|              compiler is required.                 |
|                                                    |
|               Cancel with CTRL+C                   |
######################################################
%s%s"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print header % (TermColors.MAGENTA, TermColors.BOLD,
                        TermColors.OKGREEN, TermColors.MAGENTA,
                        TermColors.ENDC, TermColors.DEFAULT)

        self.counter = 0
        self.args = parse_args()

        self.cwd = os.getcwd()
        self.inputFile = os.path.abspath(
            os.getcwd() + os.sep + self.args[1][0])

        print "%sInput file:    %s%s%s%s" % (
            TermColors.WARNING,
            TermColors.OKBLUE,
            self.inputFile,
            TermColors.DEFAULT,
            TermColors.ENDC
        )

        if len(self.args[1]) < 2:
            tmpFile = self.inputFile.split(os.sep).pop()
            self.outFile = "%s%s%s" % (os.getcwd(),
                                       os.sep,
                                       tmpFile.replace('.less', '.css')
                                       )
        else:
            self.outFile = os.path.abspath(self.args[1][1])

        self.readDir = os.sep.join(self.inputFile.split(os.sep)[:-1])
        print "%sBase dir:      %s%s%s%s" % (
            TermColors.WARNING,
            TermColors.OKBLUE,
            self.readDir,
            TermColors.DEFAULT,
            TermColors.ENDC
        )

        print "%sWill generate: %s%s%s%s" % (
            TermColors.WARNING,
            TermColors.OKBLUE,
            self.outFile,
            TermColors.DEFAULT,
            TermColors.ENDC
        )

        if self.args[0].compress:
            print "%s%s+CSS compression is enabled%s%s\n" % (
                TermColors.OKGREEN,
                TermColors.BOLD,
                TermColors.DEFAULT,
                TermColors.ENDC
            )

        try:
            raw_input("Hit %sEnter%s to start!\n" % (
                TermColors.BOLD,
                TermColors.ENDC))
        except KeyboardInterrupt:
            self.quit()

        self.firstRun = True
        self.loop()

    def getFileList(self):
        # Get the list from master file.
        includes = self.parseFile(self.inputFile)
        # Also include the "master" file.
        includes.append(self.inputFile.split(os.sep).pop())

        for idx, val in enumerate(includes):
            includes[idx] = os.path.abspath(self.readDir + os.sep + val)

        # Make sure the list is unique
        includes = list(set(includes))

        # Parse each file
        for filename in includes:
            newEl = self.parseFile(filename)
            for el in newEl:
                el = os.path.abspath('/'.join(
                    filename.split('/')[:-1]
                    ) + os.sep + el)
                if el not in includes:
                    includes.append(el)  # Add the others to parse as well.

        # Paranoia: Just to make sure the list is unique... (should be!)
        includes = list(set(includes))
        return includes

    def parseFile(self, filename, directory=None):

        try:
            fd = open(filename, 'r')
        except:
            print "%sError: Could not open:\n%s%s%s\nfor reading." % (
                TermColors.FAIL,
                TermColors.WARNING,
                filename,
                TermColors.FAIL
            )
            sys.exit(1)

        searchString = '.*@import.*[\'\"](.*)[\'\"]'
        data = fd.read()
        results = re.findall(searchString, data)
        fd.close()
        if results:
            return results
        else:
            return []

    def readFiles(self):
        if self.firstRun is False:
            print "%s%sReparsing all dependencies...%s\n" % (
                TermColors.OKGREEN,
                TermColors.BOLD,
                TermColors.ENDC)

        fileList = self.getFileList()
        self.itemList = []

        for filename in fileList:
            if filename.endswith('.less'):
                t = os.path.getmtime(filename)
                self.itemList.append({'filename': filename, 'time': t})
                if self.firstRun is True:
                    print "%s%s[Checking]: %s%s%s" % (
                        TermColors.OKGREEN,
                        TermColors.BOLD,
                        TermColors.ENDC,
                        TermColors.WARNING,
                        filename)
        self.firstRun = False

    def loop(self):
        self.readFiles()
        change = False
        cnt = 0
        try:
            while change is False:
                self.showProgress()
                for item in self.itemList:
                    if os.path.getmtime(item['filename']) != item['time']:
                        change = True
                        filemodified = item['filename'].split(os.sep).pop()
                        print "\n%sChange noticed in: %s %s" % (
                            TermColors.WARNING,
                            TermColors.OKGREEN,
                            filemodified
                        )
                time.sleep(0.3)
        except KeyboardInterrupt:
            self.quit()

        self.generate(filemodified)

    def generate(self, filemodified):
        if self.args[0].compress is True:
            args = "lessc -x %s %s" % (self.inputFile, self.outFile)
        else:
            args = "lessc %s %s" % (self.inputFile, self.outFile)
        try:
            s_val = subprocess.call(args.split(' '))

        except OSError:
            print TermColors.FAIL + 'Something went wrong!'
            sys.exit(1)

        if s_val == 0:
            if self.args[0].compress is True:
                print "\n%sSaved: %s%s %s(compressed)\n" % (
                    TermColors.WARNING,
                    TermColors.HEADER,
                    self.outFile.split(os.sep).pop(),
                    TermColors.OKBLUE
                )
            else:
                print "\n%sSaved: %s%s\n" % (
                    TermColors.WARNING,
                    TermColors.HEADER,
                    self.outFile.split(os.sep).pop()
                )

        else:
            print "%sSyntax error in file, perhaps: %s%s%s%s?%s - " \
                  "See the message above." % (
                      TermColors.FAIL,
                      TermColors.WARNING,
                      TermColors.BOLD,
                      filemodified,
                      TermColors.ENDC,
                      TermColors.DEFAULT
                      )
        self.loop()

    def quit(self):
        print "\n%sGoodbye, have a fantastic day!\n" % (TermColors.OKBLUE)
        sys.exit(0)

    def showProgress(self):
        sys.stdout.write("%s%sListening for changes %s%s%s%s\r" % (
            TermColors.OKGREEN,
            TermColors.ENDC,
            TermColors.MAGENTA,
            TermColors.BOLD,
            LessListener.anim[self.counter],
            TermColors.OKGREEN
            ))
        sys.stdout.flush()
        self.counter += 1
        if self.counter == len(LessListener.anim):
            LessListener.anim = list(reversed(LessListener.anim))
            self.counter = 0

if __name__ == '__main__':
    L = LessListener()
    L.startup()
    

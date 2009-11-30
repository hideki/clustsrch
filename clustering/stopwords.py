#!/usr/bin/python

import os
import singleton

class Stopwords(singleton.Singleton):
    _stopwords = None
    def __init__(self, filename='stopwords.txt'):
        if self._stopwords == None:
            path = os.path.join(os.path.dirname(__file__), filename)
            self._stopwords = self._loadStopwords(path)

    def stopwords(self):
        return self._stopwords

    def isStopword(self, word):
        return word in self._stopwords

    def _loadStopwords(self, filename):
        stopwords = []
        FILE = open(filename, 'r')
        while FILE:
            line = FILE.readline()
            if len(line) == 0:
                break
            stopwords.append(line.strip())
        FILE.close()
        return set([word.lower() for word in stopwords if word !=''])

def main():
    a = Stopwords()
    b = Stopwords()
    print id(a) == id(b)
    print a.stopwords() == b.stopwords()
    print "the => " + str(a.isStopword('the'))
    print "yahoo => " + str(a.isStopword('yahoo'))

if __name__ == '__main__':
    main()

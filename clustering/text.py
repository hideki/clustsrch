#!/usr/bin/env python

import re
import stopwords

def wordcount(words):
    wc = {}
    for word in words:
        wc.setdefault(word, 0.0)
        wc[word] += 1.0
    return wc

def tokenize(text):
    return cleanwords(re.split('\W+', text))

def cleanwords(words):
    return _filterStopwords(_normalize(_filterEmptyWords(words)))

def _filterStopwords(words):
    stopwordlist = stopwords.Stopwords().stopwords()
    return filter(lambda x: x not in stopwordlist, words)

def _filterEmptyWords(words):
    return filter(lambda x: len(x) > 0, words)

def _normalize(words):
    return map(lambda x: re.compile('<[^>]+>').sub('', x.lower()), words)

def main():
    print wordcount(['a', 'a', 'b', 'c', 'dd', 'ab'])
    print _filterStopwords(['a', 'the', 'b', 'yahoo', 'search', 'clustering'])
    print tokenize('<b>Yahoo!</b> is a search engine company, isn\'t it? Google too.')

if __name__ == '__main__':
    main()

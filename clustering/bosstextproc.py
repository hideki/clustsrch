#!/usr/bin/python

import re
import math
import text


def textprocess(results, termweight='tfidf'):
    # word count list
    wordcounts = []

    # df: document frequenty
    df = {}

    # iterate Y! BOSS results
    for result in results:
        # word list
        words = []
        # title
        words.extend(text.tokenize(result['title']))
        # abstract
        words.extend(text.tokenize(result['abstract']))
        # key terms of Yahoo! BOSS results
        if 'keyterms' in result and len(result['keyterms']) > 0:
            words.extend(text.cleanwords(_keyterms(result['keyterms']['terms'])))
        # del.icio.us tags of Yahoo! BOSS results
        if 'delicious_toptags' in result and len(result['delicious_toptags']) > 0:
            words.extend(text.cleanwords(_delicioustags(result['delicious_toptags']['tags'])))
        # word count from word list
        wc = text.wordcount(words)
        wordcounts.append(wc)
        # calcurate document frequncy
        for word, c in wc.items():
            df.setdefault(word, 0.0)
            df[word] += 1.0

    # word list
    wordlist = []        
    for word, freq in df.items():
        #if freq > 1.0 and float(freq)/len(results) <= 0.6:
        if freq > 1.0:
            wordlist.append(word)
    
    #print "|D|:%d" % (len(results))
    doc_count = float(len(results))

    # generate word vector 
    wordvectors = []
    for wc in wordcounts:
        doc_size = float(sum([i for i in wc.values()]))
        #print "docsize:%d" % (docsize)
        wordvector = []
        for word in wordlist:
            if word in wc:
                # boolean
                if termweight == 'boolean':
                    wordvector.append(1.0)
                # tf
                elif termweight == 'tf':
                    wordvector.append(wc[word])
                # normtf
                elif termweight == 'normtf':
                    tf  = wc[word] / doc_size
                    wordvector.append(tf)
                # tfidf
                elif termweight == 'tfidf':
                    tf  = wc[word] / doc_size
                    idf = math.sqrt(doc_count / df[word])
                    tfidf = tf * idf
                    wordvector.append(tfidf)
            else:
                wordvector.append(0.0)
        wordvectors.append(wordvector)

    #print wordlist
    #print wordvectors
    return wordlist, wordvectors

def _delicioustags(tags):
    list = []
    map(lambda tag: list.extend(re.compile('\W+').split(tag['name'])), tags)
    return list

def _keyterms(terms):
    list = []
    map(lambda term: list.extend(re.compile('\W+').split(term)), terms)
    return list


#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Hideki Itakura (h.itakura@yahoo.com)"

import sys
import bossapi
import bosstextproc
import cluster

def main(argv):
    query = reduce(lambda x, y: x + " " + y ,argv[1:])
    results = bossapi.search(query, 'web', 100)
    if len(results) == 0:
        print "0 results"
    else:
        wordlist,wordvectors = bosstextproc.textprocess(results)
        clust = cluster.hcluster(wordvectors)
        cluster.printcluster(clust,results, wordlist)

if __name__ == '__main__':
    main(sys.argv)

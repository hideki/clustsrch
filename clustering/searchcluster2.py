#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Hideki Itakura (h.itakura@yahoo.com)"

import sys
import bossapiv2
import bosstextproc
import cluster
import distance

def main(argv):
    query = reduce(lambda x, y: x + " " + y ,argv[1:])
    results = bossapiv2.search(query, 20)
    if len(results) == 0:
        print "0 results"
    else:
        wordlist,wordvectors = bosstextproc.textprocess(results) 
        clusts = cluster.hcluster(rows=wordvectors)
        clusts = cluster.divide(clusts[0], threshold=1.15)
        clusts = cluster.sortBySmallestId(clusts)
        cluster.printclusters(clusts, results, wordlist)

if __name__ == '__main__':
    main(sys.argv)

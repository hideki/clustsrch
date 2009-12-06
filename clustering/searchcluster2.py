#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Hideki Itakura (h.itakura@yahoo.com)"

import sys
import bossapi
import bosstextproc
import cluster
import distance

def main(argv):
    query = reduce(lambda x, y: x + " " + y ,argv[1:])
    results = bossapi.search(query, 'web', 50)
    if len(results) == 0:
        print "0 results"
    else:
        wordlist,wordvectors = bosstextproc.textprocess(results) 
        clusts = cluster.hcluster(rows=wordvectors)
        clusts = cluster.divide(clusts[0], threshold=0.85)
        clusts = cluster.sortBySmallestId(clusts)
        #clusts = cluster.hcluster(rows=wordvectors, distance=distance.pearson, threshold=0.85)
        #clusts = cluster.hcluster(rows=wordvectors, distance=distance.cosine, threshold=0.50)
        #clusts = cluster.sortBySmallestId(clusts)
        #cluster.printcluster(clusts[0], results, wordlist)
        cluster.printclusters(clusts, results, wordlist)

if __name__ == '__main__':
    main(sys.argv)

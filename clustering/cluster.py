#!/usr/bin/env python
# -*- coding: utf-8 -*-


import distance

class cluster(object):
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.vec      = vec
        self.left     = left
        self.right    = right
        self.distance = distance
        self.id       = id

def hcluster(rows, distance=distance.pearson):
    distances = {}
    currentclusterid = -1

    # clusters are initially just the rows 
    clusters = [cluster(rows[i], id=i) for i in range(len(rows))]

    while len(clusters) > 1:
        lowestpair = (0, 1)
        closest = distance(clusters[0].vec, clusters[1].vec)

        # loop through every pair looking for the smallest distance
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                # distances is the cache of distance calcurations
                if (clusters[i].id, clusters[j].id) not in distances:
                    distances[(clusters[i].id, clusters[j].id)] = distance(clusters[i].vec, clusters[j].vec)
                dist = distances[ (clusters[i].id, clusters[j].id) ]
                if dist < closest:
                    closest = dist
                    lowestpair = (i, j)

        # calculate the average of the two clusters
        #mergevec = _mergeVector2Ave(clusters, lowestpair)
        mergevec = _mergeVectorAllAve(clusters, lowestpair)

        # create the new cluster
        newcluster = cluster(mergevec, left=clusters[lowestpair[0]], right=clusters[lowestpair[1]], distance=closest, id=currentclusterid)

        # cluster ids that weren't in the original set are negative
        currentclusterid -= 1
        del clusters[lowestpair[1]]
        del clusters[lowestpair[0]]
        clusters.append(newcluster)

    return clusters[0]

def _mergeVector2Ave(clusters, lowestpair):
    mergevec = [ (clusters[lowestpair[0]].vec[i] + clusters[lowestpair[1]].vec[i]) / 2.0 for i in range(len(clusters[0].vec))]
    return mergevec

def _mergeVectorAllAve(clusters, lowestpair):
    mergevec = []
    for k in range(len(clusters[0].vec)):
        (sum0, count0) = _treesum(clusters[lowestpair[0]], k)
        (sum1, count1) = _treesum(clusters[lowestpair[1]], k)
        score =  (sum0 + sum1) / (count0 + count1)
        mergevec.append(score)
    return mergevec


def _treesum(cluster, i):
    if cluster.id >= 0:
        return (cluster.vec[i], 1.0)
    if cluster.left != None:
        (sumL, countL) = _treesum(cluster.left, i)
    if cluster.right != None:
        (sumR, countR) = _treesum(cluster.right, i)
    return (sumL+sumR, countL+countR)

def printcluster(cluster, results=None, wordlist=None, n = 0):
    print ' ' * n,
    if cluster.id < 0:
        # negative id means that this is branch
        keys = topIndexes(cluster.vec, 5)
        print '+ ',
        for key in keys:
            print wordlist[key] + ", ",
        print "(" + str(cluster.distance) + ")"
    else: 
        # postive id means that this is an endpoint
        if results == None:
            print cluster.id
        else:
            result = results[cluster.id]
            try:
                print str(cluster.id) + ": " + result['title'] + " (" + result['url'] + ")"
            except UnicodeEncodeError:
                print str(cluster.id) + ": " + "??????????" + " (" + result['url'] + ")"
            #print str(cluster.id) + ": " + result['title']
    
    # print the left and right branch
    if cluster.left != None:
        printcluster(cluster.left, results=results,wordlist=wordlist, n = n + 1)
    if cluster.right != None:
        printcluster(cluster.right, results=results,wordlist=wordlist, n = n + 1)
        
def topIndexes(list, n):
    if len(list) < n:
        n = len(list)
    newlist = []
    for i in range(len(list)):
        newlist.append((i, list[i]))
    newlist = sorted(newlist, key=lambda x:(x[1], x[0]), reverse=True)
    return [ newlist[i][0] for i in range(n)]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import distance
import mutualinformation

class cluster(object):
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None, smallest_id=None, size=None):
        self.vec         = vec
        self.left        = left
        self.right       = right
        self.distance    = distance
        self.id          = id
        self.smallest_id = smallest_id
        self.size        = size

def hcluster(rows, distance=distance.pearson, threshold=sys.maxint, maxclusters=sys.maxint):
    distances = {}
    currentclusterid = -1

    # clusters are initially just the rows 
    clusters = [cluster(rows[i], id=i, smallest_id=i, size=1) for i in range(len(rows))]

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

        # stop clustering if closest distance is larger than threshold
        # and num of clusters is less than miximum cluster counts
        if closest > threshold and len(clusters) <= maxclusters:
          break

        # calculate the average of the two clusters
        #mergevec = _mergeVector2Ave(clusters, lowestpair)
        mergevec = _mergeVectorAllAve(clusters, lowestpair)

        # create the new cluster
        newcluster = cluster(
            mergevec,
            left=clusters[lowestpair[0]],
            right=clusters[lowestpair[1]],
            distance=closest,
            id=currentclusterid,
            smallest_id=min(clusters[lowestpair[0]].smallest_id, clusters[lowestpair[1]].smallest_id),
            size=sum([clusters[lowestpair[0]].size, clusters[lowestpair[1]].size]))

        # cluster ids that weren't in the original set are negative
        currentclusterid -= 1
        del clusters[lowestpair[1]]
        del clusters[lowestpair[0]]
        clusters.append(newcluster)

    return clusters


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

def topNIds(cluster, n):
  ids = []
  _traverseIds(cluster, ids)
  ids.sort()
  return ids[:n]

def _traverseIds(cluster, ids):
    if cluster.id >= 0:
      ids.append(cluster.id)
    if cluster.left != None:
      _traverseIds(cluster.left, ids)
    if cluster.right != None:
      _traverseIds(cluster.right, ids)

def sortBySmallestId(clusters):
  clusters.sort(cmp=lambda x,y: cmp(x.smallest_id, y.smallest_id))
  return clusters
  
def divide(cluster, threshold):
  clusters = []
  _divide(cluster, threshold, clusters)
  return clusters

def _divide(cluster, threshold, clusters):
    if cluster.id >= 0 or cluster.distance <= threshold:
      clusters.append(cluster)
      return

    if cluster.left != None:
      _divide(cluster.left, threshold, clusters)

    if cluster.right != None:
      _divide(cluster.right, threshold, clusters)
  
def _calcurate_mi(clusters, cluster_index):
  features = map(lambda feature: {'N00':0, 'N01': 0, 'N10':0, 'N11':0}, clusters[0].vec)
  for i in range(len(clusters)):
    cluster = clusters[i]
    if i == cluster_index:
      _traverse_mi(cluster, features, True)
    else:
      _traverse_mi(cluster, features, False)
  mi_scores = map(lambda feature: mutualinformation.mi(float(feature['N11']), float(feature['N01']),float(feature['N10']),float(feature['N00'])), features)
  return mi_scores

def _traverse_mi(cluster, features, isClass):
  if cluster.id >= 0:
    for i in range(len(cluster.vec)):
      val = cluster.vec[i]
      if val == 0.0 and isClass == False:
        features[i]['N00'] += 1
      if val == 0.0 and isClass == True:
        features[i]['N01'] += 1
      if val >  0.0 and isClass == False:
        features[i]['N10'] += 1
      if val >  0.0 and isClass == True:
        features[i]['N11'] += 1

  if cluster.left != None:
    _traverse_mi(cluster.left, features, isClass)
  if cluster.right != None:
    _traverse_mi(cluster.right, features, isClass)


def printclusters(clusters, results=None, wordlist=None, n = 0):
  i = 0
  for clust in clusters:
    print "SMALLEST_ID=%s SIZE=%d" % (str(clust.smallest_id), clust.size)
    top_ids = topNIds(clust, 5)
    print top_ids
    #mi_scores = _calcurate_mi(clusters, i)
    #keys = keyTermIdxs(mi_scores, 10)
    #for key in keys:
    #  print wordlist[key] + ", ",
    #print ""
    printcluster(clust, results,wordlist,n)
    print ""
    i+=1

def printcluster(cluster, results=None, wordlist=None, n = 0):
    print ' ' * n,
    if cluster.id < 0:
        # negative id means that this is branch
        keys = keyTermIdxs(cluster.vec, 5)
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
    
    # print the left and right branch
    if cluster.left != None:
        printcluster(cluster.left, results=results,wordlist=wordlist, n = n + 1)
    if cluster.right != None:
        printcluster(cluster.right, results=results,wordlist=wordlist, n = n + 1)
        
def keyTermIdxs(list, n):
    if len(list) < n:
        n = len(list)
    newlist = []
    for i in range(len(list)):
        newlist.append((i, list[i]))
    newlist = sorted(newlist, key=lambda x:(x[1], x[0]), reverse=True)
    return [newlist[i][0] for i in range(n)]

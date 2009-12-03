import os
import logging
import pickle

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from clustering import bossapi
from clustering import bosstextproc
from clustering import cluster
from clustering import distance

class Cluster(object):
  def __init__(self, index, label):
    self.index = index
    self.label = label

class ClusterModel(db.Model):
  query   = db.StringProperty()
  results = db.BlobProperty()
  wordlist= db.StringListProperty()
  clusts  = db.BlobProperty()
  date    = db.DateTimeProperty(auto_now_add=True)

class IndexPage(webapp.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'templates')
    path = os.path.join(path, 'index.html')
    self.response.out.write(template.render(path, template_values))

class SearchPage(webapp.RequestHandler):
  def get(self):
    query = self.request.get('query')

    # check db with query as key

    results = bossapi.search(query, 'web', 100)
    if len(results) == 0:
      pass
    else:
      wordlist,wordvectors = bosstextproc.textprocess(results)
      clusts = cluster.hcluster(rows=wordvectors,distance=distance.pearson, threshold=0.84)
      clusts = cluster.sortBySmallestId(clusts)
      cluster_model = ClusterModel()
      cluster_model.query   = query
      cluster_model.results = pickle.dumps(results)
      cluster_model.wordlist = wordlist
      cluster_model.clusts = pickle.dumps(clusts)
      cluster_key = cluster_model.put()

      labels = []
      i = 0
      for clust in clusts:
        keys = cluster.keyTermIdxs(clust.vec, 2)
        label = wordlist[keys[0]] + ", " + wordlist[keys[1]]
        label += " (" + str(clust.size) + ")"
        labels.append(Cluster(i, label))
        i += 1

      template_values = {
        'cluster_key': str(cluster_key),
        'query': query,
        'results': results[:10],
        'labels': labels,
        'hits': len(results)
      }
      path = os.path.join(os.path.dirname(__file__), 'templates')
      path = os.path.join(path, 'search.html')
      self.response.out.write(template.render(path, template_values))

class ClusterPage(webapp.RequestHandler):
  def get(self):
    cluster_key = db.Key(encoded = self.request.get('cluster_key'))
    cluster_id = self.request.get('cluster_id')

    cluster_model = db.get(cluster_key)
    query = cluster_model.query
    results = pickle.loads(cluster_model.results)
    wordlist = cluster_model.wordlist
    clusts = pickle.loads(cluster_model.clusts)

    if int(cluster_id) == -1:
        cluster_results = results[:10]
    else:
      clust = clusts[int(cluster_id)]
      ids = cluster.topNIds(clust, 10)
      cluster_results = []
      for id in ids:
        cluster_results.append(results[id])

    labels = []
    i = 0
    for clust in clusts:
      keys = cluster.keyTermIdxs(clust.vec, 2)
      label = wordlist[keys[0]] + ", " + wordlist[keys[1]]
      label += " (" + str(clust.size) + ")"
      labels.append(Cluster(i, label))
      i += 1

    template_values = {
      'cluster_key': str(cluster_key),
      'query': query,
      'results': cluster_results,
      'labels': labels,
      'hits': len(results)
    }
    path = os.path.join(os.path.dirname(__file__), 'templates')
    path = os.path.join(path, 'search.html')
    self.response.out.write(template.render(path, template_values))


apps_binding = []
apps_binding.append(('/', IndexPage))
apps_binding.append(('/search', SearchPage))
apps_binding.append(('/cluster', ClusterPage))
application = webapp.WSGIApplication(apps_binding, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

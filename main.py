import logging
import md5
import os
import pickle
import re

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from clustering import bossapi
from clustering import bosstextproc
from clustering import cluster
from clustering import distance

class Cluster(object):
  def __init__(self, index, label, selected):
    self.index = index
    self.label = label
    self.selected = selected

class ClusterModel(db.Model):
  query_md5 = db.StringProperty()
  query     = db.StringProperty()
  results   = db.BlobProperty()
  wordlist  = db.StringListProperty()
  clusts    = db.BlobProperty()
  date      = db.DateTimeProperty(auto_now_add=True)

class IndexPage(webapp.RequestHandler):
  def get(self):
    _render(self, 'index.html', {})

class SearchPage(webapp.RequestHandler):
  def get(self):
    query = self.request.get('query')
    if query == None:
      self.redirect("/")
      return
    query = query.strip()
    if len(query) == 0:
      self.redirect("/")
      return
    query = re.sub('\s+', ' ', query)
    query_md5 = md5.new(query).hexdigest()

    cluster_model = db.GqlQuery("SELECT * FROM ClusterModel WHERE query_md5 = :1", query_md5).get()
    if cluster_model == None:
      results = bossapi.search(query, 'web', 100)
      if len(results) == 0:
        self.redirect("/")
        return
      else:
        wordlist, wordvectors = bosstextproc.textprocess(results)
        clusts = cluster.hcluster(rows=wordvectors,distance=distance.pearson, threshold=0.88)
        clusts = cluster.sortBySmallestId(clusts)
        cluster_model = ClusterModel()
        cluster_model.query      = query
        cluster_model.query_md5  = query_md5
        cluster_model.results    = pickle.dumps(results)
        cluster_model.wordlist   = wordlist
        cluster_model.clusts     = pickle.dumps(clusts)
        cluster_model.put()
    else:
      wordlist = cluster_model.wordlist
      results  = pickle.loads(cluster_model.results)
      clusts   = pickle.loads(cluster_model.clusts)

    labels = []
    i = 0
    for clust in clusts:
      keys = cluster.keyTermIdxs(clust.vec, 2)
      label = wordlist[keys[0]] + ", " + wordlist[keys[1]]
      label += " (" + str(clust.size) + ")"
      labels.append(Cluster(i, label, ''))
      i += 1

    template_values = {
      'all':       True,
      'query':     query,
      'query_md5': query_md5,
      'results':   results[:10],
      'labels':    labels,
      'hits':      len(results)
    }
    _render(self, 'search.html', template_values)

class ClusterPage(webapp.RequestHandler):
  def get(self):
    query_md5  = self.request.get('query_md5')
    cluster_model = db.GqlQuery("SELECT * FROM ClusterModel WHERE query_md5 = :1", query_md5).get()
    query    = cluster_model.query
    wordlist = cluster_model.wordlist
    results  = pickle.loads(cluster_model.results)
    clusts   = pickle.loads(cluster_model.clusts)

    cluster_id = self.request.get('cluster_id')
    if int(cluster_id) == -1:
      cluster_results = results[:10]
      all = True
    else:
      all = None
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
      if i == int(cluster_id):
        labels.append(Cluster(i, label,'selected'))
      else:
        labels.append(Cluster(i, label,''))
      i += 1

    template_values = {
      'all': all,
      'query': query,
      'query_md5': query_md5,
      'results': cluster_results,
      'labels': labels,
      'hits': len(results)
    }
    _render(self, 'search.html', template_values)

def _render(request_handler, template_file, template_values):
  path = os.path.join(os.path.dirname(__file__), 'templates')
  path = os.path.join(path, template_file)
  request_handler.response.out.write(template.render(path, template_values))

apps_binding = []
apps_binding.append(('/', IndexPage))
apps_binding.append(('/search', SearchPage))
apps_binding.append(('/cluster', ClusterPage))
application = webapp.WSGIApplication(apps_binding, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

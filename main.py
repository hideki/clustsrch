# -*- coding: utf-8 -*-

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '1.2')


import datetime
import logging
import math
import md5
import os
import pickle
import re

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from clustering import bossapiv2
from clustering import bosstextproc
from clustering import cluster
from clustering import distance

# Cluster representative for UI
class Cluster(object):
  def __init__(self, index, label, selected):
    self.index = index
    self.label = label
    self.selected = selected

# Cluster representative for DB
class ClusterModel(db.Model):
  query_md5 = db.StringProperty()
  query     = db.StringProperty()
  results   = db.BlobProperty()
  wordlist  = db.StringListProperty()
  clusts    = db.BlobProperty()
  date      = db.DateTimeProperty(auto_now_add=True)


# Base Page
class _BasePage(webapp.RequestHandler):
  def _view(self, query, query_md5, cluster_id, sub_cluster_id, page, cluster_model):
    # cluster
    query    = cluster_model.query
    wordlist = cluster_model.wordlist
    results  = pickle.loads(cluster_model.results)
    clusts   = pickle.loads(cluster_model.clusts)
    labels = self._labels(clusts, wordlist, cluster_id)

    # sub cluster
    if cluster_id >= 0:
      sub_clusts = cluster.divide(clusts[cluster_id], 0.85)
      sub_clusts = cluster.sortBySmallestId(sub_clusts)
      sub_labels = self._labels(sub_clusts, wordlist, sub_cluster_id)
    else:
      sub_labels = []

    # all
    if cluster_id == -1:
      selected_all = True
      selected_cluster = False
      selected_sub_cluster = False
      display_results = results
    else:
      # cluster
      if sub_cluster_id == -1:
        selected_all = False
        selected_cluster = True
        selected_sub_cluster = False
        clust = clusts[cluster_id]
        ids = cluster.topNIds(clust, clust.size)
        display_results = []
        for id in ids:
          display_results.append(results[id])
      # sub cluster
      else:
        selected_all = False
        selected_cluster = False
        selected_sub_cluster = True
        clust = sub_clusts[sub_cluster_id]
      # search results for cluster
      ids = cluster.topNIds(clust, clust.size)
      display_results = []
      for id in ids:
        display_results.append(results[id])

    #paging
    if cluster_id == -1:
      pages = self._pages(len(results), page)
    else:
      pages = self._pages(clust.size, page)
    start = (page - 1) * 10
    end   = page * 10
    if len(pages) > 1:
      paging = True
    else:
      paging = False

    template_values = {
      'selected_all': selected_all,
      'selected_cluster': selected_cluster,
      'selected_subcluster': False,
      'cluster_id': cluster_id,
      'sub_cluster_id': sub_cluster_id,
      'query': query,
      'query_md5': query_md5,
      'hits': len(results),
      'pages':   pages,
      'paging': paging,
      'labels': labels,
      'sublabels': sub_labels,
      'results': display_results[start:end],
    }
    self._render('search.html', template_values)

  def _pages(self, page_count, page):
    pages = []
    for i in range(int(math.ceil(page_count/10.0))):
      if page == i+1:
        pages.append((str(i + 1), True))
      else:
        pages.append((str(i + 1), False))
    return pages
  
  def _labels(self, clusts, wordlist, selected_cluster_id):
    labels = []
    i = 0
    for clust in clusts:
      keys = cluster.keyTermIdxs(clust.vec, 2)
      label = wordlist[keys[0]] + ", " + wordlist[keys[1]]
      label += " (" + str(clust.size) + ")"
      if i == selected_cluster_id:
        labels.append(Cluster(i, label,'selected'))
      else:
        labels.append(Cluster(i, label,''))
      i += 1
    return labels
  
  def _render(self, template_file, template_values):
    path = os.path.join(os.path.dirname(__file__), 'templates')
    path = os.path.join(path, template_file)
    self.response.out.write(template.render(path, template_values))

# Index/Main Page
class IndexPage(_BasePage):
  def get(self):
    self._render('index.html', {})

# Search/Cluster Page
class SearchPage(_BasePage):
  def get(self):
    # query 
    query, query_md5 = self._query()
    cluster_id       = -1
    sub_cluster_id   = -1
    page             = 1
    # cluster
    cluster_model = db.GqlQuery("SELECT * FROM ClusterModel WHERE query_md5 = :1", query_md5).get()
    # search & clustering
    if cluster_model == None:
      cluster_model = self._search_and_cluster(query, query_md5)
      if cluster_model == None:
        return
    # view
    self._view(query, query_md5, cluster_id, sub_cluster_id, page, cluster_model)

  def _query(self):
    query = self.request.get('query').encode('utf-8')
    if query == None:
      self.redirect("/")
      return
    query = query.strip()
    if len(query) == 0:
      self.redirect("/")
      return
    query = re.sub('\s+', ' ', query)
    query_md5 = md5.new(query).hexdigest()
    return query, query_md5

  def _search_and_cluster(self, query, query_md5):
    results = bossapiv2.search(query, 100)
    if len(results) == 0:
      self.redirect("/")
      return None
    else:
      wordlist, wordvectors = bosstextproc.textprocess(results)
      clusts = cluster.hcluster(rows=wordvectors,distance=distance.pearson, threshold=1.03)
      clusts = cluster.sortBySmallestId(clusts)
      cluster_model = ClusterModel()
      cluster_model.query      = query.decode('utf-8')
      cluster_model.query_md5  = query_md5
      cluster_model.results    = pickle.dumps(results)
      cluster_model.wordlist   = wordlist
      cluster_model.clusts     = pickle.dumps(clusts)
      cluster_model.put()
    return cluster_model


#class ClusterPage(webapp.RequestHandler):
class ClusterPage(_BasePage):
  def get(self):
    # url params
    query_md5      = self.request.get('query_md5')
    cluster_id     = int(self.request.get('cluster_id'))
    sub_cluster_id = int(self.request.get('sub_cluster_id'))
    page           = int(self.request.get('page'))

    # cluster
    cluster_model = db.GqlQuery("SELECT * FROM ClusterModel WHERE query_md5 = :1", query_md5).get()
    query    = cluster_model.query
    #view
    self._view(query, query_md5, cluster_id, sub_cluster_id, page, cluster_model)

class DeleteCache(webapp.RequestHandler):
    def get(self) :
        date = datetime.datetime.now() - datetime.timedelta(1, 0);
        modelset = ClusterModel.all().filter('date <', date)
        for model in modelset:
            model.delete()

class RemoveAll(webapp.RequestHandler):
    def get(self) :
        limit = 10
        list=self.getMyList(limit)
        if len(list)<1:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write( 'OK remove all data.' )
            return 
        for c in list:
            c.delete()
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write( '<html>' )
        self.response.out.write( '<head>' )
        self.response.out.write( '<META HTTP-EQUIV="REFRESH" CONTENT="10;URL=/removeall">')
        self.response.out.write( '</head>' )
        self.response.out.write( '<body>' )
        self.response.out.write( 'Again after 10seconds.' )
        self.response.out.write( '</body>' )
        self.response.out.write( '</html>' )

    def getMyList(self,limit):
        query = ClusterModel.gql('LIMIT '+str(limit))
        return query[0:min(query.count(),limit)]

apps_binding = []
apps_binding.append(('/',                  IndexPage))
apps_binding.append(('/search',            SearchPage))
apps_binding.append(('/cluster',           ClusterPage))
apps_binding.append(('/removeall',         RemoveAll))
apps_binding.append(('/tasks/deletecache', DeleteCache))
application = webapp.WSGIApplication(apps_binding, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

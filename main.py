import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from clustering import bossapi
from clustering import bosstextproc
from clustering import cluster
from clustering import distance

class SearchPage(webapp.RequestHandler):
  def get(self):
    q = self.request.get('q')
    if q:
      self.search(q)
    else: 
      self.index()

  def search(self, q):
    results = bossapi.search(q, 'web', 100)
    if len(results) == 0:
      pass
    else:
        wordlist,wordvectors = bosstextproc.textprocess(results)
        clusts = cluster.hcluster(rows=wordvectors,distance=distance.pearson, threshold=0.84)
        #clusts = cluster.hcluster(rows=wordvectors,distance=distance.cosine, threshold=0.50)
        clusts = cluster.sortBySmallestId(clusts)
        labels = []
        for clust in clusts:
          keys = cluster.keyTermIdxs(clust.vec, 2)
          label = wordlist[keys[0]] + ", " + wordlist[keys[1]]
          label += " (" + str(clust.size) + ")"
          labels.append(label)
        template_values = {
          'query': q,
          'results': results[:10],
          'labels': labels
        }
        path = os.path.join(os.path.dirname(__file__), 'templates')
        path = os.path.join(path, 'search.html')
        self.response.out.write(template.render(path, template_values))

  def index(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'templates')
    path = os.path.join(path, 'index.html')
    self.response.out.write(template.render(path, template_values))

apps_binding = []
apps_binding.append(('/', SearchPage))
application = webapp.WSGIApplication(apps_binding, debug=True)

def main():
  run_wsgi_app(application)
    

if __name__ == '__main__':
  main()

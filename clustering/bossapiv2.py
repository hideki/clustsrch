#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib
import simplejson
from google.appengine.api import urlfetch
import oauth.oauth as oauth

OAUTH_CONSUMER_KEY    = "<oauth consumer key>"
OAUTH_CONSUMER_SECRET = "<oauth consumer secret>"
SEARCH_API_URL        = 'http://yboss.yahooapis.com/ysearch/limitedweb'
#SEARCH_API_URL        = 'http://yboss.yahooapis.com/ysearch/web'
MAX_SEARCH_PER_REQUEST = 5


def _search(q, start=0, count=50):
    data = {
        "q":      q,
        "start":  start,
        "count":  count, # 35 for images
        "format": "json",
    }
    consumer = oauth.OAuthConsumer(OAUTH_CONSUMER_KEY, OAUTH_CONSUMER_SECRET)
    signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
    signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=None, http_method='GET', http_url=SEARCH_API_URL, parameters=data)
    oauth_request.sign_request(signature_method_hmac_sha1, consumer, "")
    complete_url = oauth_request.to_url()
    #print >> sys.stderr, "url=[%s]" % (complete_url)
    result = urlfetch.fetch(complete_url)
    #print >> sys.stderr, "result=[%s]" % (result.content)
    if result.status_code == 200:
   	    return simplejson.loads(result.content)
    else:
        return None

def search(query, total_req_size = 50):
    """ retrieve search results from Y! Search BOSS """
    #print >> sys.stderr, "query=[%s]" % (query)
    results  = []
    total_res_size = 0
    i = 0
    while total_res_size < total_req_size:
        i += 1
        if i >= MAX_SEARCH_PER_REQUEST:
			break
        req_size = min(total_req_size - total_res_size, 50)
        response = _search(q=query, start=total_res_size, count=req_size)
        if response == None:
            continue
        count    = int(response['bossresponse']['limitedweb']['count'])
        #count    = int(response['bossresponse']['web']['count'])
        if count == 0:
            break
        results.extend(response['bossresponse']['limitedweb']['results'])
        #results.extend(response['bossresponse']['web']['results'])
        total_res_size += count
        if count < req_size:
            break
    return results

def dumpBossResults(results):
    pos = 0
    for result in results:
        print "pos => "      + str(pos)
        if 'url' in result:
            print "\turl => "      + result['url']
        if 'title' in result:
            print "\ttitle => "    + result['title']
        if 'abstract' in result:
            try:
                print "\tabstract => " + result['abstract']
            except UnicodeEncodeError:
                print "\tabstract => ERROR"
        print ""
        pos+=1

def dumpBossResponse(response):
    start = response['ysearchresponse']['start']
    count = response['ysearchresponse']['count']
    print "start => "      + start
    print "count => "      + count
    dumpBossResults(response['ysearchresponse']['resultset_web'])

def main():
    dumpBossResults(search("steve jobs", 100))
	#print _search("webos", 0, 10)

if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import simplejson

APP_ID         = '<APP_ID>'
SEARCH_API_URL = 'http://boss.yahooapis.com/ysearch/%s/v%d/%s?format=json&start=%d&count=%d&lang=%s&region=%s&appid=' + APP_ID

def _params(d):
    p = ""
    for k, v in d.iteritems():
        p += "&%s=%s" % (urllib.quote_plus(k), urllib.quote_plus(v))
    return p

def _search(query, vertical="web", version=1, start=0, count=50, lang="en", region="us", more={}):
    url = SEARCH_API_URL % (vertical, version, urllib.quote_plus(query), start, count, lang, region) + _params(more)
    print url
    return simplejson.load(urllib.urlopen(url))

def search(query, vertical="web", total_req_size = 100):
    """ retrieve search results from Y! Search BOSS """

    attrs = {}
    # for web search
    if vertical =="web":
        #attrs['abstract'] = 'long'
        attrs['view'] = 'keyterms,delicious_toptags,delicious_saves'

    results  = []
    total_res_size = 0
    while total_res_size < total_req_size:
        req_size = min(total_req_size - total_res_size, 50)
        response = _search(query=query, vertical=vertical, start=total_res_size, count=req_size, more=attrs)
        count    = int(response['ysearchresponse']['count'])
        if count == 0:
            break
        if vertical == 'web':
            results.extend(response['ysearchresponse']['resultset_web'])
        elif vertical == 'news':
            results.extend(response['ysearchresponse']['resultset_news'])
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
        if 'keyterms' in result:
            print "\tkeyterms => " + str(result['keyterms'])
        if 'delicious_toptags' in result:
            print "\ttags => "     + str(result['delicious_toptags'])
        if 'delicious_saves' in result:
            print "\tsaves => "    + str(result['delicious_saves'])
        print ""
        pos+=1

def dumpBossResponse(response):
    start = response['ysearchresponse']['start']
    count = response['ysearchresponse']['count']
    print "start => "      + start
    print "count => "      + count
    dumpBossResults(response['ysearchresponse']['resultset_web'])

def main():
    dumpBossResults(search("グーグル", 'web', 5))

if __name__ == '__main__':
    main()

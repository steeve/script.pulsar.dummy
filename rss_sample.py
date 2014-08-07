import sys
import json
import base64
import re
import urllib
import urllib2
import xml.etree.ElementTree as ET

PAYLOAD = json.loads(base64.b64decode(sys.argv[1]))
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.66 Safari/537.36"

def _text(node, path):
    n = node.find(path)
    if n is not None:
        return n.text
def _attr(node, path, attrib):
    n = node.find(path)
    if n is not None:
        return n.attrib.get(attrib)

def search(query):
    req = urllib2.Request("http://foo.bar/search/%s" % urllib.quote_plus(query))
    req.add_header("User-Agent", USER_AGENT)
    response = urllib2.urlopen(req)
    root = ET.fromstring(response.read())
    return [{
        "uri": _attr(item, ".//enclosure", "url"),
        "name": _text(item, ".//title"),
        "info_hash": _text(item, ".//info_hash"),
    } for item in root.getiterator("item")]

def search_episode(imdb_id, tvdb_id, name, season, episode):
    return search("%s S%02dE%02d" % (name, season, episode))

def search_movie(imdb_id, name, year):
    return search("%s %s" % (name, year))

urllib2.urlopen(
    PAYLOAD["callback_url"],
    data=json.dumps(globals()[PAYLOAD["method"]](*PAYLOAD["args"]))
)

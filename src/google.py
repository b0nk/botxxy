import urllib
import json
from mylib import unescape

g_logo = "12G4o8o12g9l4e"


def webSearch(terms):
  g_baseURL = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&"

  query = urllib.urlencode({'q': terms})
  data = urllib.urlopen(g_baseURL + query).read()
  j = json.loads(data)
  res = j['responseData']['results']
  output = []
  for i in res:
    title = i['title'].replace("<b>", "").replace("</b>", "")
    title = unescape(title)
    url = i['url']
    url = urllib.unquote(url)
    string = "%s: %s ( %s )" % (g_logo, title, url)
    output.append(string)

  return output


def imageSearch(terms):
  g_baseURL = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&"

  query = urllib.urlencode({'q': terms})
  data = urllib.urlopen(g_baseURL + query).read()
  j = json.loads(data)
  res = j['responseData']['results']
  output = []

  for i in res:
    string = "%s Images: %s (%sx%s)" % (g_logo, i['unescapedUrl'], i['width'], i['height'])
    output.append(string)

  return output

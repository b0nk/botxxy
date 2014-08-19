import feedparser


def getLatest():
  feed = feedparser.parse("http://rss.thepiratebay.se/0")

  title = feed['entries'][0]['title']
  link = feed['entries'][0]['comments'].replace('http://', 'https://')

  return "%s - %s" % (title, link)

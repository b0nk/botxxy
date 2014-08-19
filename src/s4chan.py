import urllib
import json
from mylib import unescape, stripHTML

logo = '3::54chan'


def format(comment):

  comment = unescape(comment)
  comment = comment.replace('<br>', ' ')
  comment = comment.replace('<wbr>', '')
  # greentext open
  comment = comment.replace('<span class="quote">', '3')
  # greentext open
  comment = comment.replace('<span class="deadlink">', '3')
  # close color
  comment = comment.replace('</span>', '')
  # remove the rest of html tags
  comment = stripHTML(comment)

  return comment


def search(board, search):
  res = []

  try:
    catalog = json.load(urllib.urlopen('https://a.4cdn.org/%s/catalog.json' % board))

    for i in catalog:
      for j in i['threads']:
        if search.lower() in j.get('sub', '').lower() or search.lower() in j.get('com', '').lower():
          subject = j.get('sub', 'Empty subject')
          subject = unescape(subject)
          post = j.get('com', 'Empty post')
          post = format(post)

          if len(post) > 100:
            # close color here also
            post = post[0:100] + '...'

          boardLink = 'https://boards.4chan.org/%s/thread/%s' % (board, j['no'])

          text = '%s /%s/ | %s | %s | %s (R:%s, I:%s)' % (logo, board, subject, post, boardLink, j['replies'], j['images'])
          res.append(text)
    return res
  except(IOError):
    return ['%s Error: Try again later' % logo]


def getValidBoards():
  boards = []

  l = json.load(urllib.urlopen('https://a.4cdn.org/boards.json'))

  for i in l['boards']:
    boards.append(str(i['board']))

  return boards


def getThreadInfo(board, threadNo):
  info = json.load(urllib.urlopen('https://a.4cdn.org/%s/thread/%s.json' % (board, threadNo)))

  op = info['posts'][0]

  name = op.get('name', 'Anonymous')
  subject = op.get('sub', 'Empty subject')
  subject = unescape(subject)
  post = op.get('com', 'Empty post')
  post = format(post)

  if len(post) > 100:
    # close color here also
    post = post[0:100] + '...'

  return "%s /%s/ | %s | %s | %s | (R:%s, I:%s)" % (logo, board, name, subject, post, op['replies'], op['images'])

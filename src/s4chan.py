import urllib, json
from mylib import unescape, stripHTML

def search(board, search):
  logo = '3::54chan'
  res = []

  try:
    catalog = json.load(urllib.urlopen('https://api.4chan.org/%s/catalog.json' % board))
  
    for i in catalog:
      for j in i['threads']:
        if search.lower() in j.get('sub', '').lower() or search.lower() in j.get('com', '').lower():
          subject = j.get('sub', 'Empty subject')
          subject = unescape(subject)
          post = j.get('com', 'Empty post')
          post = unescape(post)
          post = post.replace('<br>', ' ')
          post = post.replace('<wbr>', '')
          post = post.replace('<span class="quote">', '3') #greentext open
          post = post.replace('<span class="deadlink">', '3') #greentext open
          post = post.replace('</span>', '') #close color
          post = stripHTML(post) #remove the rest of html tags
  
          if len(post) > 300:
            post = post[0:300] + '...' #close color here also
            
          boardLink = 'https://boards.4chan.org/%s/res/%s' % (board, j['no'])
  
          text = '%s /%s/ %s | %s | %s (R:%s, I:%s)' % (logo, board, subject, post, boardLink, j['replies'], j['images'])
          res.append(text)
    return res
  except(IOError):
    return ['%s Error: Try again later' % logo]

def getValidBoards():
  boards = []

  l = json.load(urllib.urlopen('https://api.4chan.org/boards.json'))

  for i in l['boards']:
    boards.append(str(i['board']))

  return boards

import requests
import bs4

from mylib import stripHTML, unescape

def getGames():
  soup  = bs4.BeautifulSoup(requests.get("http://humblebundle.com").text)
  games = [ unescape(str.strip(stripHTML(str(i)))) for i in soup.find_all('span', 'item-title') if str.strip(stripHTML(str(i))) is not '' ]
  
  return ", ".join(games)

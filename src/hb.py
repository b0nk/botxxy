import requests
import bs4

from mylib import stripHTML

def getGames():
  soup  = bs4.BeautifulSoup(requests.get("http://humblebundle.com").text)
  games = [str.strip(stripHTML(str(i))) for i in soup.find_all('span', 'item-title')]
  
  return ", ".join(games)

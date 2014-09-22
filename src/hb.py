import requests
import bs4


def getGames():

  not_games = ["Electronic Frontier Foundation",
               "American Red Cross",
               "Child's Play Charity",
               "More games coming soon!"]
  games = []

  soup = bs4.BeautifulSoup(requests.get("https://humblebundle.com").text)
  for i in soup.find_all('span', 'game-box'):
    game = i.find('img')['alt']
    if game not in not_games and "Soundtrack" not in game:
      games.append(game)

  return ", ".join(games)

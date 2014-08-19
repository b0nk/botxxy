# FMylife module for python bots by Aha2Y.
import urllib
from bs4 import BeautifulSoup


class Quote():
  def __init__(self, number, text, disagree, agree):
      self.number, self.text, self.disagree, self.agree = number, text, disagree, agree


def get():
  rscript_fml = urllib.urlopen("http://rscript.org/lookup.php?type=fml")
  fml = BeautifulSoup(rscript_fml)

  text = fml.pre.string.split("\n")[4][1:][5:]
  number = fml.pre.string.split("\n")[2][5:]
  agree = fml.pre.string.split("\n")[5]
  disagree = fml.pre.string.split("\n")[6]
  q = Quote(number, text, agree, disagree)
  return q

import re
import htmlentitydefs


def unescape(text):
  def fixup(m):
    text = m.group(0)
    if text[:2] == "&#":
      # character reference
      try:
        if text[:3] == "&#x":
          return unichr(int(text[3:-1], 16))
        else:
          return unichr(int(text[2:-1]))
      except ValueError:
        pass
    else:
      # named entity
      try:
        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
      except KeyError:
        pass
    # leave as is
    return text
  return re.sub("&#?\w+;", fixup, text)


def stripHTML(html):
  return re.sub('<[^<]+?>', '', html)


def myprint(msg):
  prompt = '>> '
  print "%s%s" % (prompt, msg)

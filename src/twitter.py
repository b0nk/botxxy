import pytwitter
import apikeys
import time
import datetime
from mylib import unescape, myprint

t_logo = "0,10twitter"

t_api = pytwitter.Api(consumer_key=apikeys.TWT_CON_KEY,
                      consumer_secret=apikeys.TWT_CON_SEC,
                      access_token_key=apikeys.TWT_TOK_KEY,
                      access_token_secret=apikeys.TWT_TOK_SEC)


def getTweet(user, n):
  now = int(time.time())
  try:
    t_user = t_api.GetUser(None, user)._screen_name
    tweets = t_api.GetUserTimeline(screen_name=t_user, count=200)

    if not tweets:
      return "%s User: %s has no tweets" % (t_logo, t_user)

    else:
      tweet = tweets[n].GetText()
      t = int(tweets[n].GetCreatedAtInSeconds())
      created = "Posted %s ago" % (datetime.timedelta(seconds=now - t))
      tweet = unescape(tweet).replace('\n', ' ')
      return "%s @%s: %s (%s)" % (t_logo, t_user, tweet, created)

  except pytwitter.TwitterError as e:
    myprint("TwitterError: %s" % (e))
    return "%s Error: Nope." % (t_logo)
  except IndexError:
    return "%s Error: You have gone too far (keep below 200)" % (t_logo)


def search(query, n):
  try:
    results = t_api.GetSearch(term=query, result_type="recent", count=15)
    if not results:
      return "%s No results for %s" % (t_logo, query)
    else:
      user = results[n].GetUser()._screen_name
      tweet = unescape(results[n].GetText()).replace('\n', ' ')
      return "%s @%s: %s" % (t_logo, user, tweet)
  except IndexError:
    return "%s Error: YOU'VE GONE TOO FAR (keep below 15)" % (t_logo)

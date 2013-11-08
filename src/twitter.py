import pytwitter
import time
import datetime
from mylib import unescape

  
def getTweet(user, n):
  now = int(time.time())
  t_logo = "0,10twitter"
  try:
    t_api = pytwitter.Api(consumer_key = '***REMOVED***',
                          consumer_secret = '***REMOVED***',
                          access_token_key = '***REMOVED***',
                          access_token_secret = '***REMOVED***')
    
    t_user = t_api.GetUser(None, user)._screen_name
    tweets = t_api.GetUserTimeline(screen_name = t_user, count = 200)
    
    if not tweets:
      return "%s User: %s has no tweets" % (t_logo, t_user)
      
    else:
      tweet = tweets[n].GetText()
      t = int(tweets[n].GetCreatedAtInSeconds())
      created = "Posted " + str(datetime.timedelta(seconds=now-t)) + " ago"
      tweet = unescape(tweet).replace('\n', ' ')
      return "%s @%s: %s (%s)" % (t_logo, t_user, tweet, created)
      
  except pytwitter.TwitterError as e:
    return "%s Error: %s" % (t_logo, e)
  except IndexError:
    return "%s Error: You have gone too far (keep below 200)" % (t_logo)

# https://tools.ietf.org/html/rfc1459
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
# http://forum.codecall.net/topic/59608-developing-a-basic-irc-bot-with-python/
# http://docs.python.org/2/library/ssl.html
# http://docs.python.org/2/library/hashlib.html
# https://www.hackthissite.org/articles/read/1050
# http://stackoverflow.com/questions/4719438/editing-specific-line-in-text-file-in-python

'''
@author: b0nk
@version: 2.0
'''

# Import the necessary libraries.
import socket
import ssl
import hashlib
import time
import random
import sys

import mylogger
sys.stdout = mylogger.Logger()
sys.stderr = mylogger.Logger()

from mylib import unescape, myprint, stripHTML

import apikeys

# URL spoiler
import httplib2
import re
import bs4
import urlparse

# Other imports
# Imports for last.fm methods
# https://code.google.com/p/pylast/
import pylast

# Imports for google search
import google

# Imports for feeds
# Twitter
# https://github.com/bear/python-twitter
# https://github.com/simplegeo/python-oauth2
import twitter

# Fuck my life
# http://www.hawkee.com/snippet/9431/
import fml

# 4chan search
import s4chan

# Humble Bundle
import hb

# Piratebay Roulette
import tpb

# Some basic variables used to configure the bot

server = "irc.catiechat.net"
# default port
port = 6667
# ssl port
ssl_port = 6697
# default channels
chans = ["#test"]
botnick = "botxxy"
botuser = "I"
bothost = "m.botxxy.you.see"
botserver = "testserver"
botname = "testname"
botpassword = "bawksy"
quitmsg = "Exited normally!"

# Global vars

nicks = []

authDB = []
authUsrs = []
ignUsrs = []
greets = []
eightball = []
quotes = []
lfmUsers = []
cakeDeaths = []

taggers = []
tagged = ''
prevTagged = ''
isTagOn = False
lastCommand = ''
tmpstr = ''
rosestr = "3---<-<-{4@"
boobsstr = "(.Y.)"
cakestr_0 = "    _|||||_"
cakestr_1 = "   {~*~*~*~}"
cakestr_2 = " __{*~*~*~*}__ "
cakestr_3 = "`-------------`"

# Last.fm vars

lfm_logo = "0,5last.fm"
cmp_bars = ["[4====            ]",
            "[4====7====        ]",
            "[4====7====8====    ]",
            "[4====7====8====9====]",
            "[                ]"]
lastfm = None

# Google vars
g_logo = "12G4o8o12g9l4e"

# Twitter vars
t_logo = "0,10twitter"

# URL spoiler
urlpat = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
yt_logo = "0,4You1,0Tube"

# Internet
h = httplib2.Http(disable_ssl_certificate_validation=True, timeout=10)
userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0'
def_headers = {'user-agent': userAgent}

# 4chan vars
chanLogo = '3::54chan'
validBoards = []

# ============BASIC FUNCTIONS TO MAKE THIS A BIT EASIER===============


# This is our first function! It will respond to server Pings.
def ping(reply):
  # In some IRCds it is mandatory to reply to PING the same message we recieve
  ircsock.send("PONG :%s\n" % (reply))
  # DEBUG:
  # myprint("PONG :%s" % (reply))


# This sends a message to the channel 'chan'
def sendChanMsg(chan, msg):
  try:
    ircsock.send("PRIVMSG %s :%s\n" % (chan, msg.encode("utf8")))
  except UnicodeDecodeError:
    ircsock.send("PRIVMSG %s :%s\n" % (chan, msg))


# This sends a notice to the nickname 'nick'
def sendNickMsg(nick, msg):
  try:
    ircsock.send("NOTICE %s :%s\n" % (nick, msg.encode("utf8")))
  except UnicodeDecodeError:
    ircsock.send("NOTICE %s :%s\n" % (nick, msg))


# Returns the nickname of whoever requested a command from a RAW irc privmsg. Example in commentary below.
def getNick(msg):
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split('!')[0].replace(':', '')


# Returns the user and host of whoever requested a command from a RAW irc privmsg. Example in commentary below.
def getUser(msg):
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split(" PRIVMSG ")[0].translate(None, ':')


# Returns the channel from whereever a command was requested from a RAW irc PRIVMSG. Example in commentary below.
def getChannel(msg):
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split(" PRIVMSG ")[-1].split(' :')[0]


# This function is used to join channels.
def joinChan(chan):
  ircsock.send("JOIN %s\n" % (chan))


# This is used to join all the channels in the array 'chans'
def joinChans(chans):
  for i in chans:
    ircsock.send("JOIN %s\n" % (i))


# This function responds to a user that inputs "Hello botxxy"
def hello(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    chan = getChannel(msg)
    myprint("%s said hi in %s" % (nick, chan))
    sendChanMsg(chan, "Hello %s! Type !help for more information." % (nick))


def identify(again):
  # Here we actually assign the nick to the bot
  ircsock.send("NICK %s\n" % (botnick))
  time.sleep(3)
  # Identifies the bot's nickname with nickserv
  ircsock.send("NICKSERV IDENTIFY %s\n" % (botpassword))
  myprint("Bot identified")
  if again:
    joinChans(chans)


def resetLog():
  with open("botlog.log", "w") as f:
    f.write('')
    f.close
  myprint("Log reset!")

# ========================END OF BASIC FUNCTIONS=====================

# ========================INITIALIZATIONS============================


# Authorized
def loadAuth():
  global authDB
  try:
    authDB = [line.strip() for line in open('auth.txt', 'r')]
    myprint("Auth -> Loaded")
  except IOError as e:
    myprint("Auth -> FAIL | %s" % e)
    authDB = []


# Ignores
def loadIgn():
  global ignUsrs
  try:
    ignUsrs = [line.strip() for line in open('ign.txt', 'r')]
    myprint("Ign -> %s" % ignUsrs)
  except IOError as e:
    myprint("Ign -> FAIL | %s" % e)
    ignUsrs = []


# Greets
def loadGreets():
  global greets
  try:
    greets = [line.strip() for line in open('greet.txt', 'r')]
    myprint("Greets -> Loaded")
  except IOError as e:
    myprint("Greets -> FAIL | %s" % e)
    greets = []


# 8ball
def load8ball():
  global eightball
  try:
    eightball = [line.strip() for line in open('8ball.txt', 'r')]
    myprint("8ball -> Loaded")
  except IOError as e:
    myprint("8ball -> FAIL | %s" % e)
    eightball = []


# Quotes
def loadQuotes():
  global quotes
  try:
    quotes = [line.strip() for line in open('quotes.txt', 'r')]
    myprint("Quotes -> Loaded")
  except IOError as e:
    myprint("Quotes -> FAIL | %s" % e)
    quotes = []


# Cakes
def loadCakes():
  global cakeDeaths
  try:
    cakeDeaths = [line.strip() for line in open('cake.txt', 'r')]
    myprint("Cake -> Loaded")
  except IOError as e:
    myprint("Cake -> FAIL | %s" % e)
    cakeDeaths = []


# Last.fm Users
def loadLfmUsers():
  global lfmUsers
  try:
    lfmUsers = [line.strip() for line in open('lfmusers.txt', 'r')]
    myprint("LfmUsers -> Loaded")
  except IOError as e:
    myprint("LfmUsers -> FAIL | %s" % e)
    lfmUsers = []


def loadLfm():
  global lastfm
  API_KEY = apikeys.LFM_KEY
  API_SEC = apikeys.LFM_SEC
  lastfm = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SEC, username='', password_hash='')
  myprint("last.fm API -> Loaded")


# 4chan board list
def loadValidBoards():
  global validBoards
  validBoards = s4chan.getValidBoards()
  myprint("Valid boards -> %s" % validBoards)


# ========================END OF INITIALIZATIONS=====================

# AUTHENTICATION
def authCmd(msg):
  nick = getNick(msg)
  if nick not in ignUsrs:
    global authDB, authUsrs
    if '#' in msg.split(':')[1]:
      chan = getChannel(msg)
      for i, content in enumerate(authDB):
        if nick + "|!|" in content:
          authDB[i] = None
          authDB.remove(None)
          authUsrs.remove(nick)
          myprint(str(authDB))
          with open("auth.txt", 'w') as f:
            for i in authDB:
              f.write('%s\n' % i)
              f.closed

          sendChanMsg(chan, "Password deleted you dumbass!!!")
          sendNickMsg(nick, "Request a new password.")
    else:
      # ":b0nk!LoC@fake.dimension PRIVMSG :!pass password"
      # RAW password
      password = msg.split("!pass")[1].lstrip(' ')
      if not password:
        sendNickMsg(nick, "Bad arguments. Usage: !pass <password>")
      else:
        # A HEX representation of the SHA-256 encrypted password
        password = hashlib.sha256(password).hexdigest()
        myprint("ENC: %s" % (password))

        for i, content in enumerate(authDB):
          if nick + "|!|" + password in content:
            authUsrs.append(nick)
            myprint("%s is authorized." % (nick))
            myprint(str(authUsrs))
            sendNickMsg(nick, "Password correct.")
            return None

        myprint("%s mistyped the password" % (nick))
        sendNickMsg(nick, "Password incorrect!")


# INVITE
# Parses the message to extract NICK and CHANNEL
def inviteCmd(msg):
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :!invite "
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !invite outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!invite")[1].lstrip(' ')
      # Checks if user inserted a nickname to invite
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !invite <nick>")
      else:
        # Success
        myprint("Inviting %s to channel %s" % (target, chan))
        sendChanMsg(chan, "Inviting %s here..." % (target))
        invite(target, chan)


# Invites given nickname to present channel
def invite(nick, chan):
  ircsock.send("INVITE %s %s\n" % (nick, chan))


# VOICE
def voiceCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !voice outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!voice")[1].lstrip(' ')
      # Checks if user inserted a nickname to voice
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !voice <nick>")
      else:
        # Success
        myprint("Voicing %s on channel %s" % (target, chan))
        voice(target, chan)


def voice(nick, chan):
  ircsock.send("MODE %s +v %s\n" % (chan, nick))


# DEVOICE
def devoiceCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !devoice outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!devoice")[1].lstrip(' ')
      # Checks if user inserted a nickname to devoice
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !devoice <nick>")
      elif target != botnick:
        # Success
        myprint("Devoicing %s on channel %s" % (target, chan))
        devoice(target, chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")


def devoice(nick, chan):
  ircsock.send("MODE %s -v %s\n" % (chan, nick))


# OP
def opCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !op outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!op")[1].lstrip(' ')
      # Checks if user inserted a nickname to op
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !op <nick>")
      else:
        # Success
        myprint("Giving op to %s on channel %s" % (target, chan))
        op(target, chan)


def op(nick, chan):
  ircsock.send("MODE %s +o %s\n" % (chan, nick))


# DEOP
def deopCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !deop outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!deop")[1].lstrip(' ')
      # Checks if user inserted a nickname to deop
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !deop <nick>")
      elif target != botnick:
        # Success
        myprint("Taking op from %s on channel %s" % (target, chan))
        deop(target, chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")


def deop(nick, chan):
  ircsock.send("MODE %s -o %s\n" % (chan, nick))


# HOP
def hopCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !hop outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!hop")[1].lstrip(' ')
      # Checks if user inserted a nickname to hop
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !hop <nick>")
      else:
        # Success
        myprint("Giving hop to %s on channel %s" % (target, chan))
        hop(target, chan)


def hop(nick, chan):
  ircsock.send("MODE %s +h %s\n" % (chan, nick))


# DEHOP
def dehopCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !dehop outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!dehop")[1].lstrip(' ')
      # Checks if user inserted a nickname to dehop
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !dehop <nick>")
      elif target != botnick:
        # Success
        myprint("Taking hop from %s on channel %s" % (target, chan))
        dehop(target, chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")


def dehop(nick, chan):
  ircsock.send("MODE %s -h %s\n" % (chan, nick))


# TOPIC
def topicCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !topic outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      # ":b0nk!LoC@fake.dimension PRIVMSG #test :!topic 1 2 3 test"
      topic = msg.split("!topic")[1].lstrip(' ')
      if not topic:
        myprint("New topic is empty")
        sendChanMsg(chan, "Bad arguments. Usage: !topic [<new topic>]")
      else:
        myprint("%s changed %s's topic to '%s'" % (nick, chan, topic))
        changeTopic(chan, topic)


def changeTopic(chan, topic):
  ircsock.send("TOPIC %s :%s\n" % (chan, topic))


# KICK
def kickCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !kick outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!kick")[1].lstrip(' ')
      # Checks if user inserted a nickname to kick
      if not target:
        sendChanMsg(chan, "Bad arguments. Usage: !kick <nick>")
      elif target == botnick:
        myprint("%s tried to kick the bot!" % (nick))
        sendChanMsg(chan, "Don't make me kick myself out %s!" % (nick))
      else:
        myprint("Kicking %s from %s..." % (target, chan))
        kick(target, chan, 0)


def kick(nick, chan, isRand):
  if isRand:
    sendChanMsg(chan, "Randomly kicking %s from %s" % (nick, chan))
    ircsock.send("KICK %s %s :lol butthurt\n" % (chan, nick))
  else:
    sendChanMsg(chan, "Kicking %s from %s" % (nick, chan))
    ircsock.send("KICK %s %s :lol butthurt\n" % (chan, nick))


# RANDOM KICK
def randKick(nicks, chan):
  # Correcting offset (this means if we have an array with 5 elements we should pick a random number between 0 and 4)
  size = len(nicks) - 1
  # Picks a random number
  rand = random.randint(0, size)
  # Prevents bot from being kicked by !randkick
  if botnick not in nicks[rand]:
    myprint("Randomly kicking %s from %s" % (nicks[rand], chan))
    kick(nicks[rand], chan, 1)
  else:
    myprint("Bot will not be kicked. Picking another one...")
    randKick(nicks, chan)


# IGNORE
def ignCmd(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs and nick in authUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      target = msg.split(":!ign")[1].lstrip(' ')
      if target:
        ign(nick, target)


def ign(nick, target):
  global ignUsrs
  ignUsrs.append(target)
  with open("ign.txt", 'w') as f:
    for elem in ignUsrs:
      f.write("%s\n" % elem)
  f.closed
  sendNickMsg(nick, "%s ignored!" % (target))
  myprint("Ign -> %s" % (str(ignUsrs)))


# DICE
def dice(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    chan = getChannel(msg)
    # converts the integer dice to a string to be concatenated in the final output
    dice = random.randint(1,6)
    myprint("%s rolled the dice and got a %d" % (nick, dice))
    sendChanMsg(chan, "%s rolled a %d" % (nick, dice))


# QUOTES
# TODO: quote IDs
def quoteCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !quote outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      # ":b0nk!LoC@fake.dimension PRIVMSG #test :!quote random"
      '''
      if not msg.split("!quote")[1] or not msg.split("!quote ")[1]:
        sendChanMsg(chan,"Bad arguments. Usage: !quote num/random")
      else:
        quoteNum = msg.split("!quote ")[1]
        if quoteNum == "random":
      '''
      global quotes
      line = random.choice(quotes)
      if line:
        author = line.split("|!|")[0]
        quote = line.split("|!|")[1]
        # debugging
        myprint("%s | %s" % (author, quote))
        sendChanMsg(chan, "[Quote] %s" % (quote))
      else:
        myprint("File quotes.txt is empty")
        sendChanMsg(chan, "There are no quotes on the DB. Could something be wrong???")


def addQuote(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs:
    # Checks if quote was sent outside of a channel
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !addquote outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      # ":b0nk!LoC@fake.dimension PRIVMSG #test :!quote random"
      newQuote = msg.split("!addquote")[1].lstrip(' ')
      # Checks for empty quote
      if not newQuote:
        sendChanMsg(chan, "Bad arguments. Usage: !addquote [<quote>]")
      else:
        global quotes
        quotes.append(nick + "|!|" + newQuote)
        myprint("%s added '%s'" % (nick, newQuote))
        with open("quotes.txt", 'w') as f:
          for i in quotes:
            f.write("%s\n" % i)
        f.closed
        sendChanMsg(chan, "Quote added!")


# BLUEBERRYFOX
def bbfquotes(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !blueberry outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      myprint("Sending blueberryfox's fav quotes to %s" % (chan))
      sendChanMsg(chan, "Blueberryfoxes favorite Quotes: One, two, three, four, I declare a thumb war, five, six, seven, eight I use this hand to masturbate")
      time.sleep(1)
      sendChanMsg(chan, "I was like ohho!")
      time.sleep(1)
      sendChanMsg(chan, "I love your hair")


# GREET MESSAGES
def setGreetCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    # let's make sure people use this privately so that people won't see the welcoming message until they join a channel
    if '#' in msg.split(':')[1]:
      chan = getChannel(msg)
      myprint("%s sent !setjoinmsg in %s. Sending warning..." % (nick, chan))
      sendChanMsg(chan, "Don't do that in the channel %s" % (nick))
      sendNickMsg(nick, "Send it as a notice or query(pvt)")
    else:
      # Retrieves the entry message
      newMsg = msg.split(":!setjoinmsg")[1].lstrip(' ')
      # Checks if entry message is empty
      if not newMsg:
        # if empty we send False to setGreet so the bot knows the user wants to unset his greet
        setGreet(nick, newMsg, False)
      else:
        # in this case the user wants to change or create an entry message so we send True
        setGreet(nick, newMsg, True)


def setGreet(nick, newMsg, toSet):
  global greets
  changed = False
  # Here we start scanning the array
  for idx, content in enumerate(greets):
    # In this case the user already has a greet message
    if nick + "|!|" in str(content):
      # This will happen if there is a new entry message and not an empty one
      if toSet:
        # Changes the entry message to the new one
        greets[idx] = nick + "|!|" + newMsg
        myprint("Resetting %s's greet message to '%s'" % (nick, newMsg))
        sendNickMsg(nick, "Entry message re-set!")
        changed = True
        # We've found the nickname we can get out of the loop
        break
        # This will happen if there is an empty entry message on an existing nick
      else:
        # Completely erases the content
        greets[idx] = None
        greets.remove(None)
        myprint("Unsetting %s's greet message" % (nick))
        sendNickMsg(nick, "Entry message unset!")
        changed = True
        # We've found the nickname we can get out of the loop
        break
        # this will happen if there is a message and we didn't find a nickname
        # in the file which means it's the 1st time being used or it was erased previously
  if toSet and not changed:
    # Adds the nick and corresponding greet message
        greets.append(nick + "|!|" + newMsg)
        myprint("Setting %s's greet message to '%s'" % (nick, newMsg))
        sendNickMsg(nick, "Entry message set!")
  with open("greet.txt", 'w') as f:
    for i in greets:
      f.write("%s\n" % i)
  f.close()


def sendGreet(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    # ":b0nk!LoC@fake.dimension JOIN #test"
    chan = msg.split(" JOIN ")[1]
    greet = ''
    global greets
    for elem in greets:
      if nick + "|!|" in elem:
        greet = elem.split("|!|")[1]
        myprint("Greeting %s in %s" % (nick, chan))
        break
    if greet:
      sendChanMsg(chan, greet)


# TAG (play catch)
def startTag(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    # Checks of command was sent in a channel
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !starttag outside of a channel" % (nick))
      # Warned the nickname
      sendNickMsg(nick, "You are not in a channel")
    else:
      global isTagOn, tagged, taggers
      taggers.remove(botnick)
      if 'ChanServ' in taggers:
        taggers.remove('ChanServ')
        # Get the channel where the game is taking place
      chan = getChannel(msg)
      # Checks if a game is in progress
      if not isTagOn:
        # Whoever starts the game is it
        tagged = nick
        # Set game start
        isTagOn = True
        sendChanMsg(chan, "The game starts and %s is it!" % (nick))
        # Warns if game is on progress
      else:
        sendChanMsg(chan, "A game is already in progress.")


def endTag(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !endtag outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      global isTagOn, tagged
      chan = getChannel(msg)
      if isTagOn:
        isTagOn = False
        tagged = ''
        sendChanMsg(chan, "The fun is over people :( it's raining...")
      else:
        sendChanMsg(chan, "There is no game in progress!")


def tag(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !tag outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      global isTagOn, tagged, prevTagged
      if isTagOn:
        target = msg.split("!tag")[1].lstrip(' ')
        # Checks if the nick tagged nothing
        if not target:
          sendChanMsg(chan, "Tag who??? Usage: !tag <nick>")
        else:
          # Removes trailing spaces left by some clients auto-complete
          target = target.rstrip(' ')
          # Checks if the bot gets tagged
          if target is botnick:
            myprint("%s tagged the bot!" % (nick))
            sendChanMsg(chan, "%s tagged me!" % (nick))
            # Bot picks a random player to tag
            target = random.choice(taggers)
            myprint("Tagging %s..." % (target))
            tagged = target
            sendChanMsg(chan, "%s Tag! You're it!" % (target))
            prevTagged = nick
            # Target must exist in the list of players
          elif target in taggers:
            # Checks if the player is it
            if nick == tagged:
              # Checks if player is tagging himself
              if nick == target:
                myprint("%s tagged himself" % (nick))
                sendChanMsg(chan, "Don't tag yourself %s" % (nick))
              else:
                # Player tags someone other than himself or the bot
                myprint("%s tagged %s" % (tagged, target))
                tagged = target
                prevTagged = nick
                sendChanMsg(chan, "%s tagged you %s you're it!" % (nick, target))
            else:
              sendChanMsg(chan, "%s you are not it!" % (nick))
          else:
            sendChanMsg(chan, "Who are you tagging %s? Maybe %s was not here when the game started." % (nick, target))
      else:
        sendChanMsg(chan, "%s we're not playing tag now..." % (nick))


def setTagged(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !settagged outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      global isTagOn, prevTagged, tagged
      if isTagOn:
        target = msg.split("!settagged")[1].lstrip(' ')
        # Checks if the nick wrote anything to set
        if not target:
          sendChanMsg(chan, "Set who??? Usage: !settagged <nick>")
        else:
          # Removes trailing spaces left by some clients auto-complete
          target = target.rstrip(' ')
          # Target must exist in the list of players
          if target in taggers:
            if nick == prevTagged:
              if nick == target:
                myprint("%s set himself as tagged" % (nick))
                sendChanMsg(chan, "Don't tag yourself %s" % (nick))
              elif target == botnick:
                myprint("%s set the bot as tagged!" % (nick))
                sendChanMsg(chan, "%s tagged me instead!" % (nick))
                # Bot picks a random player to tag
                target = random.choice(taggers)
                myprint("Tagging %s..." % (target))
                tagged = target
                sendChanMsg(chan, "%s Tag! You're it!" % (target))
              else:
                myprint("%s decided to tag %s instead" % (nick, target))
                sendChanMsg(chan, "%s decided to tag %s instead" % (nick, target))
                tagged = target
                sendChanMsg(chan, "%s tagged you %s you're it!" % (nick, target))
            else:
              sendChanMsg(chan, "%s you were not previously it." % (nick))
          else:
            sendChanMsg(chan, "Who are you tagging %s? Maybe %s was not here when the game started." % (nick, target))
      else:
        sendChanMsg(chan, "%s we're not playing tag now..." % (nick))


# ROSE
def rose(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !rose outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!rose")[1].lstrip(' ')
      if not target:
        # Checks for a target to send a rose to
        sendChanMsg(chan, "%s don't keep the roses to yourself. Usage: !rose <nick>" % (nick))
      else:
        target = target.rstrip(' ')
        if nick == target:
          # Checks if nick is sending a rose to himself
          myprint("%s is being selfish with the roses" % (nick))
          sendChanMsg(chan, "Don't be selfish %s give that rose someone else" % (nick))
        elif target == botnick:
          myprint("%s sent a rose to the bot." % (nick))
          sendChanMsg(chan, "%s gave me a rose!" % (nick))
          sendChanMsg(chan, "[%s] %s [%s]" % (nick, rosestr, target))
          sendChanMsg(chan, ":3 thanks 4<3")
        else:
          # Success (normal case)
          myprint("%s sent a rose to %s" % (nick, target))
          sendChanMsg(chan, "%s gives a rose to %s" % (nick, target))
          sendChanMsg(chan, "[%s] %s [%s]" % (nick, rosestr, target))


# CAKE
# this function actually prints the cake, since it's a multi-line
# ascii art thing and i didn't want to rewrite its code everywhere
def printCake(chan):
  sendChanMsg(chan, cakestr_0)
  sendChanMsg(chan, cakestr_1)
  sendChanMsg(chan, cakestr_2)
  sendChanMsg(chan, cakestr_3)


def cake(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !cake outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!cake")[1].lstrip(' ')
      if not target:
        # Checks for a target to promise some cake
        sendChanMsg(chan, "%s, there is science to do. Usage: !cake <nick>" % (nick))
      else:
        target = target.rstrip(' ')
        if nick == target:
          # Checks if nick is eating the cake by himself
          myprint("%s is tricking test subjects and eating the cake" % (nick))
          sendChanMsg(chan, "Those test subjects won't test for free! %s, leave some cake for them" % (nick))
        elif target == botnick:
          myprint("%s gives some tasty cake to the bot." % (nick))
          printCake(chan)
          sendChanMsg(chan, "Thank you %s!" % (nick))
          sendChanMsg(chan, "It's so delicious and moist.")
        else:
          # Success (normal case)
          myprint("%s is sharing some cake" % (nick))
          if random.randint(1, 100) > 95:
            sendChanMsg(chan, "%s gives some tasty cake to %s" % (nick, target))
            printCake(chan)
          else:
            sendChanMsg(chan, "Unfortunately, %s %s" % (target, random.choice(cakeDeaths)))


# BOOBS
def boobs(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !boobs outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split("!boobs")[1].lstrip(' ')
      if not target:
        # Checks for a target to show boobs to
        sendChanMsg(chan, "%s don't hide those boobs. Usage: !boobs <nick>" % (nick))
      else:
        target = target.rstrip(' ')
        if nick == target:
          # Checks if nick is sending !boobs to itself
          myprint("%s is being shy with those boobs" % (nick))
          sendChanMsg(chan, "Stop looking at the mirror %s show us them boobs" % (nick))
        elif target == botnick:
          myprint("%s sent !boobs to the bot." % (nick))
          sendChanMsg(chan, "%s those are cute" % (nick))
          sendChanMsg(chan, "But mine are bigger --> ( . Y . )")
        else:
          # Success (normal case)
          myprint("%s sent !boobs to %s" % (nick, target))
          sendChanMsg(chan, "%s shows %s some boobs" % (nick, target))
          sendChanMsg(chan, "[%s] %s [%s]" % (nick, boobsstr, target))


# SAY
def sayCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' in msg.split(':')[1]:
      chan = getChannel(msg)
      myprint("%s sent !say in %s. Sending warning..." % (nick, chan))
      sendChanMsg(chan, "Don't do that in the channel %s" % (nick))
      sendNickMsg(nick, "Send it as a notice or query(pvt)")
    else:
      # ":b0nk!~LoC@fake.dimension PRIVMSG botxxy :!say #boxxy lol message"
      target = msg.split(':')[2].split(' ')[1]
      message = msg.split(target)[1].lstrip(' ')
      ircsock.send("PRIVMSG %s :%s\n" % (target, message))


# 8BALL
def eightBallCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !8ball outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      question = re.search(":!8ball (.+\?|.+ \?)", msg)
      if question:
        global eightball
        answer = random.choice(eightball)
        if answer:
          myprint("8ball says: %s" % (answer))
          sendChanMsg(chan, "%s asked [%s] the 8ball says: %s" % (nick, question.group(1), answer))
        else:
          myprint("No 8ball answers")
          sendChanMsg(chan, "No 8ball answers :(")
      else:
        myprint("%s didn't ask a question" % (nick))
        sendChanMsg(chan, "How about you ask me a question properly %s? Usage: !8ball [<question>]?" % (nick))


# LAST.FM
# this looks for the last.fm username by nick
def getLfmUser(nick):
  global lfmUsers
  user = ''
  for i in lfmUsers:
    if nick in i:
      user = i.split('|!|')[1]
  # returns empty if not found
  return user


def setLfmUserCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    lfm_username = re.search(":.setuser (\w+)?", msg)
    if not lfm_username:
      # sends false flag to unset username
      setLfmUser(nick, lfm_username, False)
    else:
      # sends true flag to set/re-set username
      setLfmUser(nick, lfm_username.group(1), True)


def setLfmUser(nick, lfm_username, toSet):
  global lfmUsers
  changed = False
  # hit detection
  for idx, content in enumerate(lfmUsers):
    # scans array
    if nick + "|!|" in str(content):
      # finds the nickname
      if toSet:
        lfmUsers[idx] = "%s|!|%s" % (nick, lfm_username)
        myprint("%s re-set it's LAST.FM username to %s" % (nick, lfm_username))
        sendNickMsg(nick, "last.fm username re-set!")
        changed = True
        # get out of loop
        break
      else:
        lfmUsers[idx] = None
        lfmUsers.remove(None)
        myprint("%s unset it's LAST.FM username" % (nick))
        sendNickMsg(nick, "last.fm username unset!")
        changed = True
        break
  if toSet and not changed:
        lfmUsers.append("%s|!|%s" % (nick, lfm_username))
        myprint("%s set it's LAST.FM username to %s" % (nick, lfm_username))
        sendNickMsg(nick, "last.fm username set!")
  with open("lfmusers.txt", 'w') as f:
    for i in lfmUsers:
      # stores data back to file
      f.write('%s\n' % i)
  f.close()


# use of the last.fm interface (pylast) in here
def compareLfmUsers(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent .compare outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      args = re.search(":.compare (\w+) (\w+)", msg)
      if args:
        # correct usage
        user1 = args.group(1)
        user2 = args.group(2)
        try:
          global lastfm
          # comparison information from pylast
          compare = lastfm.get_user(user1).compare_with_user(user2, 5)
          global cmp_bars
          # compare[0] contains a str with a num from 0-1 here we round it to 4 digits and turn it to a percentage 0-100
          index = round(float(compare[0]), 2) * 100
          if index < 1.0:
            bar = cmp_bars[4]
          else:
            # int(index / 25.01) will return an integer from 0 to 3 to choose what bar to show
            bar = cmp_bars[int(index / 25.01)]
          raw_artists = []
          # compare[1] contains an array of pylast.artist objects
          raw_artists = compare[1]
          artist_list = ''
          # users have artists in common
          if raw_artists:
            artist_list = ", ".join(i.get_name() for i in raw_artists)
          else:
            # no artists in common so we return '(None)'
            artist_list = "N/A"
          myprint("Comparison between %s and %s %d%% %s" % (user1, user2, index, artist_list))
          sendChanMsg(chan, "%s Comparison: %s %s %s - Similarity: %d%% - Common artists: %s" % (lfm_logo, user1, bar, user2, index, artist_list))
        except pylast.WSError as e:
          # catched the exception, user truly does not exist
          print e.details
          sendChanMsg(chan, "%s Error: %s" % (lfm_logo, e.details))
          return None
      else:
        myprint("%s sent bad arguments for .compare" % (nick))
        # warning for bad usage
        sendChanMsg(chan, "%s Bad arguments! Usage: .compare <username1> [username2]" % (lfm_logo))


# use of the last.fm interface (pylast) in here
def nowPlaying(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent .np outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = re.search(":.np ?(\w+)?", msg).group(1)
      if not target:
        # let's check the file
        target = getLfmUser(nick)
      if not target:
        # he is not in the db
        sendChanMsg(chan , "%s First set your username with .setuser <last.fm username>. Alternatively use .np <last.fm username>" % (lfm_logo))
        myprint("%s sent .np but is not registered" % (nick))
      else:
        try:
          global lastfm
          # returns pylast.User object
          lfm_user = lastfm.get_user(target)
          # checks if user has scrobbled anything EVER
          if lfm_user.get_playcount() < 1:
            # no need to get a nowplaying when the library is empty
            myprint("%s has an empty library" % (target))
            sendChanMsg(chan, "%s %s has an empty library" % (lfm_logo, target))
          else:
            # np is now a pylast.Track object
            np = lfm_user.get_now_playing()
            # user does not have a now listening track
            if np is None:
              myprint("%s does not seem to be playing any music right now..." % (target))
              sendChanMsg(chan, "%s %s does not seem to be playing any music right now..." % (lfm_logo, target))
            else:
              # all went well
              # string containing artist name
              artist_name = np.artist.get_name()
              # string containing track title
              track = np.title

              # here we check if the user has ever played the np track
              try:
                playCount = int(np.get_add_info(target).userplaycount)
              except (ValueError, TypeError):
                # this error means track was never played so we just say it's 1
                playCount = 1
              if playCount == 0:
                playCount = 1

              np = np.get_add_info(target)
              loved = ''

              # checks if np is a loved track to show when brodcasted to channel
              if np.userloved == '1':
                loved = "4<3 "

              tags = np.get_top_tags(5)
              # some tracks have no tags so we request the artist tags
              if not tags:
                tags = np.artist.get_top_tags(5)

              # insert number of plays to begining of tag list
              tags.insert(0, "%d plays" % playCount)
              myprint("%s is now playing: %s - %s %s(%s)" % (target, artist_name, track, loved, ", ".join(tags)))
              # broadcast to channel
              sendChanMsg(chan, "%s %s is now playing: %s - %s %s(%s)" % (lfm_logo, target, artist_name, track, loved, tags))
              # last.fm | b0nk is now playing: Joan Jett and the Blackhearts - You Want In, I Want Out (1 plays, rock, rock n roll, Joan Jett, 80s, pop)
        except pylast.WSError as e:
          # catched the exception, user truly does not exist
          print e.details
          sendChanMsg(chan, "%s Error: %s" % (lfm_logo, e.details))
          return None


# TWITTER
def getTwitter(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !twitter outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      args = re.search(":!twitter ([@#]?\w+) ?(\d+)?", msg)
      if args:
        query = args.group(1)
        index = args.group(2)
        try:
          index = int(index)
        except (ValueError, TypeError):
          index = 0
        if query[0] == "#":
          res = twitter.search(query, index)
        else:
          res = twitter.getTweet(query, index)

        myprint(res)
        sendChanMsg(chan, res)
      else:
        myprint("%s used bad arguments for !twitter" % (nick))
        sendChanMsg(chan, "%s Bad arguments! Usage: !twitter <@user | #hashtag> [optional index]" % (t_logo))


# FML
def fmlCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !fml outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      q = fml.get()
      myprint("FML | %s | %s | %s | %s" % (q.number, q.agree, q.disagree, q.text))
      sendChanMsg(chan, "%s [%s - %s]" % (q.text, q.agree, q.disagree))


# URL SPOILER
def urlSpoiler(msg):
  nick = getNick(msg)
  global ignUsrs, h, def_headers, cwf_headers
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent a URL outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      url = re.search(urlpat, msg).group(0)
      myprint("Getting title from: %s" % (url))
      try:
        r, data = h.request(url, "HEAD")
        if "text/html" in r['content-type']:
          if 'youtube.com' in urlparse.urlparse(url)[1]:
            myprint("It's a youtube link")
            r, data = h.request(url, "GET", headers=def_headers)
            soup = bs4.BeautifulSoup(data)
            url_title = stripHTML(str(soup.find('title')))
            url_title = unescape(url_title).strip().replace('\n', ' ').rstrip(' - YouTube')
            myprint("Title: %s" % (url_title))
            try:
              yt_link = 'https://youtu.be/%s' % re.search('v\=([a-zA-Z0-9-_=]+)', url).group(1)
              myprint(yt_link)
              sendChanMsg(chan, "%s's link title: %s %s | %s" % (nick, yt_logo, url_title, yt_link))
            except(IndexError, AttributeError):
              r, data = h.request(url, "GET", headers=def_headers)
              soup = bs4.BeautifulSoup(data)
              url_title = stripHTML(str(soup.find('title')))
              url_title = unescape(url_title).strip().replace('\n', ' ')
              myprint("Title: %s" % (url_title))
              sendChanMsg(chan, "%s's link title: %s %s" % (nick, yt_logo, url_title))
          elif re.search("4chan.org/(.+)/thread/(\d+)", url):
            myprint("It's a 4chan link")
            threadInfo = re.search("4chan.org/(.+)/thread/(\d+)", url)
            board = threadInfo.group(1)
            thread = threadInfo.group(2)
            url_title = s4chan.getThreadInfo(board, thread)
            myprint("4chan Title: %s" % url_title)
            sendChanMsg(chan, "%s's link title: %s" % (nick, url_title))
          else:
            r, data = h.request(url, "GET", headers=def_headers)
            soup = bs4.BeautifulSoup(data)
            url_title = stripHTML(str(soup.find('title')))
            url_title = unescape(url_title).strip().replace('\n', ' ')
            myprint("Title: %s" % (url_title))
            sendChanMsg(chan, "%s's link title: %s" % (nick, url_title))
        else:
          myprint("%s is of type %s" % (url, r['content-type']))

      except(socket.error, KeyError, AttributeError, httplib2.RedirectLimit, httplib2.ServerNotFoundError) as e:
        myprint("%s (%s)" % (url, e))
        sendChanMsg(chan, "%s's link error (%s)" % (nick, e))


# GOOGLE SEARCH
def gSearch(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !google outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      arg = re.search(":!google (.+)", msg)
      if arg:
        query = arg.group(1)
        myprint('Google web search for: %s' % (query))
        res = google.webSearch(query)
        if res:
          for i in res[0:3]:
            myprint(i)
            sendChanMsg(chan, i)
        else:
          myprint("no results for %s" % query)
          sendChanMsg(chan, "%s no results :(" % (g_logo))
      else:
        myprint("%s used bad arguments for !google" % (nick))
        sendChanMsg(chan, "%s Bad arguments! Usage: !google [search terms]" % (g_logo))


def gImageSearch(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !images outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      arg = re.search(":!images (.+)", msg)
      if arg:
        query = arg.group(1)
        myprint('Google image search for: %s' % (query))
        res = google.imageSearch(query)
        if res:
          for i in res[0:3]:
            myprint(i)
            sendChanMsg(chan, i)
        else:
          myprint("no results for %s" % query)
          sendChanMsg(chan, "%s no results :(" % (g_logo))
      else:
        myprint("%s used bad arguments for !images" % (nick))
        sendChanMsg(chan, "%s Bad arguments! Usage: !images [search terms]" % (g_logo))


# 4chan search
def chanSearch(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !4chan outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      args = re.search(":!4chan /?(\w+)/? (.+)", msg)
      if args:
        board = args.group(1)
        sterms = args.group(2)
        if board in validBoards:
          res = s4chan.search(board, sterms)
          if res:
            for i in res[0:3]:
              myprint(i)
              sendChanMsg(chan, i)
          else:
            myprint("No results for %s on /%s/" % (sterms, board))
            sendChanMsg(chan, "%s No threads on /%s/ with %s" % (chanLogo, board, sterms))
        else:
            myprint("Invalid board %s" % (board))
            sendChanMsg(chan, "%s No such board /%s/" % (chanLogo, board))
      else:
        myprint("%s used bad arguments for !4chan" % (nick))
        sendChanMsg(chan, "%s Bad arguments! Usage: !4chan <board> <search terms>" % (chanLogo))


# Humble Bundle
def humbleBundle(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !hb outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      games = hb.getGames()
      myprint(games)
      sendChanMsg(chan, games)


# Piratebay roulette
def tpbRoulette(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !tpb outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      res = tpb.getLatest()
      myprint(res)
      sendChanMsg(chan, res)


# QUIT
def quitIRC():
  myprint("Killing the bot...")
  # This kills the bot!
  ircsock.send("QUIT :%s\n" % quitmsg)


# HELP (THE WALL OF TEXT) keep this on the bottom
def helpcmd(msg):
  # Here is the help message to be sent as a private message to the user
  nick = getNick(ircmsg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs:
    myprint("Help requested by %s" % (nick))
    sendNickMsg(nick, "You have requested help.")
    # 0.5 seconds to avoid flooding
    time.sleep(0.5)
    sendNickMsg(nick, "You can say 'Hello %s' in a channel and I will respond." % (botnick))
    time.sleep(0.5)
    sendNickMsg(nick, "You can also invite me to a channel and I'll thank you for inviting me there.")
    time.sleep(0.5)
    sendNickMsg(nick, "General commands: !help !invite !rtd !quote !addquote !setjoinmsg !starttag !endtag !tag !rose !boobs !8ball !pass !cake !fml !tpb")
    time.sleep(0.5)
    sendNickMsg(nick, "%s commands: .setuser .np .compare" % (lfm_logo))
    time.sleep(0.5)
    sendNickMsg(nick, "%s commands: !twitter" % (t_logo))
    time.sleep(0.5)
    sendNickMsg(nick, "%s commands: !google !images" % (g_logo))
    time.sleep(0.5)
    sendNickMsg(nick, "%s commands: !4chan" % (chanLogo))
    if nick in authUsrs:
      sendNickMsg(nick, "Channel control commands: !op !deop !hop !dehop !voice !devoice !topic !kick !randkick")
      time.sleep(0.5)
    sendNickMsg(nick, "I'm running on python 2.7.x and if you want to contribute or just have an idea, talk to b0nk on #test .")


# Initializations
def load():
  loadAuth()
  loadIgn()
  loadGreets()
  loadQuotes()
  load8ball()
  loadLfmUsers()
  loadLfm()
  loadCakes()
  loadValidBoards()


# Connection
load()
try:
  # TODO: IPv6 ???
  ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # SSL wrapper for the socket
  ircsock = ssl.wrap_socket(ircsock)
  ircsock.settimeout(250.0)
  # Here we connect to the server using the port defined above
  ircsock.connect((server, ssl_port))
  # Bot authentication
  ircsock.send("USER %s %s %s %s\n" % (botuser, bothost, botserver, botname))
  time.sleep(3)
  # Bot identification
  # False flag means it is not a re-identification
  identify(False)
  time.sleep(3)
  joinChans(chans)
  time.sleep(3)
  stack = []

# This is our infinite loop where we'll wait for commands to show up, the 'break' function will exit the loop and end the program thus killing the bot
  while 1:
    # Receive data from the server
    stack.append(ircsock.recv(1024))
    while stack:
      ircmsg = stack.pop()
      # Removing any unnecessary linebreaks
      ircmsg = ircmsg.strip('\n\r')
      # Here we print what's coming from the server
      print ircmsg

      # If the server pings us then we've got to respond!
      if "PING :" in ircmsg:
        # In some IRCds it is mandatory to reply to PING the same message we recieve
        reply = ircmsg.split("PING :")[1]
        ping(reply)

      if " 353 " in ircmsg:
        try:
          # ":irc.catiechat.net 353 botxxy = #test :KernelPone ~b0nk CommVenus @botxxy "
          chan = ircmsg.split(" = ")[1].split(' ')[0]
          # Returns raw list of nicks
          ircmsg = ircmsg.split(':')[2]
          # Removes user mode characters
          ircmsg = ircmsg.translate(None, '~@+&%')
          # Removes an annoying SPACE char left by the server at the end of the string
          ircmsg = ircmsg.strip()
          # Puts nicks in an array
          nicks = ircmsg.split(' ')
          myprint("Nicks: %s" % nicks)
          if '353' in nicks:
            ircsock.send("NAMES " + chan + '\n')

          # Now that we have the nicks we can decide what to do with them depending on the command
          if "!randkick" in lastCommand:
            lastCommand = ''
            randKick(nicks, chan)

          if "!starttag" in lastCommand:
            lastCommand = ''
            if not isTagOn:
              taggers = nicks
              startTag(tmpstr)
              tmpstr = ''
            else:
              sendChanMsg(chan, "The game is already in progress!")
        except IndexError:
          myprint("Something went wrong...")

      if " INVITE " + botnick + " :" in ircmsg:
        tmpstr = ircmsg
        # :botxxy!~I@m.botxxy.you.see INVITE b0nk :#test
        nick = getNick(tmpstr)
        if nick not in ignUsrs:
          target = tmpstr.split(':')[2]
          myprint("%s invited the bot to %s. Joining..." % (nick, target))
          joinChan(target)
          sendChanMsg(target, "Thank you for inviting me here %s!" % (nick))
          tmpstr = ''

      hasURL = re.search(urlpat, ircmsg)

      # If we can find "Hello/Hi {botnick}" it will call the function hello(nick)
      if ":hello " + botnick in ircmsg.lower() or ":hi " + botnick in ircmsg.lower():
        hello(ircmsg)

      # checks for !help
      if ":!help" in ircmsg:
        helpcmd(ircmsg)

      if ":!ident" in ircmsg:
        user = getUser(ircmsg)
        if user == "b0nk!~LoC@fake.dimension":
          identify(True)

      if ":!newlog" in ircmsg:
        user = getUser(ircmsg)
        if user == "b0nk!~LoC@fake.dimension":
          resetLog()

      # checks for !die
      if ":!die" in ircmsg:
        user = getUser(ircmsg)
        # TODO: use auth
        if user == "b0nk!~LoC@fake.dimension":
          quitIRC()
          sys.exit(0)
        else:
          nick = getNick(ircmsg)
          myprint("%s tried to kill the bot. Sending warning..." % (nick))
          sendNickMsg(nick, "I'm afraid I can't let you do that %s..." % nick)

      # let's say it was made to reload the vars and arrays
      if ":!reload" in ircmsg:
        user = getUser(ircmsg)
        if user == "b0nk!~LoC@fake.dimension":
          load()

      if ":!invite" in ircmsg:
        inviteCmd(ircmsg)

      if ":!voice" in ircmsg:
        voiceCmd(ircmsg)

      if ":!devoice" in ircmsg:
        devoiceCmd(ircmsg)

      if ":!op" in ircmsg:
        opCmd(ircmsg)

      if ":!deop" in ircmsg:
        deopCmd(ircmsg)

      if ":!hop" in ircmsg:
        hopCmd(ircmsg)

      if ":!dehop" in ircmsg:
        dehopCmd(ircmsg)

      if ":!kick" in ircmsg:
        kickCmd(ircmsg)

      if ":!rtd" in ircmsg:
        dice(ircmsg)

      if ":!randkick" in ircmsg:
        nick = getNick(ircmsg)
        if nick not in ignUsrs:
          if '#' not in ircmsg.split(':')[1]:
            sendNickMsg(nick, "You are not in a channel!")
          else:
            chan = getChannel(ircmsg)
            ircsock.send("NAMES " + chan + '\n')
            myprint("Getting NAMES from %s" % (chan))
            lastCommand = "!randkick"

      if ":!topic" in ircmsg:
        topicCmd(ircmsg)

      if ":!pass" in ircmsg:
        authCmd(ircmsg)

      if ":!quote" in ircmsg:
        quoteCmd(ircmsg)

      if ":!addquote" in ircmsg:
        addQuote(ircmsg)

      if ":!blueberry" in ircmsg:
        # this will broadcast all of blueberrys favorite quotes :3
        bbfquotes(ircmsg)

      if " JOIN " in ircmsg:
        sendGreet(ircmsg)

      if ":!setjoinmsg" in ircmsg:
        setGreetCmd(ircmsg)

      if ":!tag" in ircmsg:
        tag(ircmsg)

      if ":!starttag" in ircmsg:
        nick = getNick(ircmsg)
        if nick not in ignUsrs:
          if '#' not in ircmsg.split(':')[1]:
            sendNickMsg(nick, "You are not in a channel!")
          else:
            chan = getChannel(ircmsg)
            ircsock.send("NAMES " + chan + '\n')
            myprint("Getting NAMES from %s" % (chan))
            lastCommand = "!starttag"
            tmpstr = ircmsg

      if ":!endtag" in ircmsg:
        endTag(ircmsg)

      if ":!settagged" in ircmsg:
        setTagged(ircmsg)

      if ":!rose" in ircmsg:
        rose(ircmsg)

      if ":!boobs" in ircmsg:
        boobs(ircmsg)

      if ":!cake" in ircmsg:
        cake(ircmsg)

      if ":!say" in ircmsg:
        sayCmd(ircmsg)

      if ":!8ball" in ircmsg:
        eightBallCmd(ircmsg)

      if ":!ign" in ircmsg:
        ignCmd(ircmsg)

      if ":.np" in ircmsg:
        nowPlaying(ircmsg)

      if ":.setuser" in ircmsg:
        setLfmUserCmd(ircmsg)

      if ":.compare" in ircmsg:
        compareLfmUsers(ircmsg)

      if ":!google" in ircmsg:
        gSearch(ircmsg)

      if ":!images" in ircmsg:
        gImageSearch(ircmsg)

      if ":!twitter" in ircmsg:
        getTwitter(ircmsg)

      if ":!fml" in ircmsg:
        fmlCmd(ircmsg)

      if ":!4chan" in ircmsg:
        chanSearch(ircmsg)

      if ":!hb" in ircmsg:
        humbleBundle(ircmsg)

      if ":!tpb" in ircmsg:
        tpbRoulette(ircmsg)

      if hasURL is not None and 'nospoil' not in ircmsg:
        urlSpoiler(ircmsg)
        hasURL = None

      if ircmsg.startswith("ERROR :Closing Link:"):
        raise socket.error('derp')

except socket.error as e:
  myprint("Bot killed / timedout (%s)" % e)
  # -1 is error exit code
  sys.exit(-1)

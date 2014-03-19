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
import urllib
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

# Some basic variables used to configure the bot

server = "irc.catiechat.net"
port = 6667 # default port
ssl_port = 6697 # ssl port
chans = ["#test", "#music", "#boxxy", "#nsfw"] #default channels
botnick = "botxxy" # bot nick
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
h = httplib2.Http(disable_ssl_certificate_validation = True, timeout = 10)
userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0'
def_headers = {'user-agent': userAgent}

#4chan vars
chanLogo = '3::54chan'
validBoards = []

#============BASIC FUNCTIONS TO MAKE THIS A BIT EASIER===============

def ping(reply): # This is our first function! It will respond to server Pings.
  ircsock.send("PONG :%s\n" % (reply)) # In some IRCds it is mandatory to reply to PING the same message we recieve
  #myprint("PONG :%s" % (reply))

def sendChanMsg(chan, msg): # This sends a message to the channel 'chan'
  try:
    ircsock.send("PRIVMSG %s :%s\n" % (chan, msg.encode("utf8")))
  except UnicodeDecodeError:
    ircsock.send("PRIVMSG %s :%s\n" % (chan, msg))
  
def sendNickMsg(nick, msg): # This sends a notice to the nickname 'nick'
  try:
    ircsock.send("NOTICE %s :%s\n" % (nick, msg.encode("utf8")))
  except UnicodeDecodeError:
    ircsock.send("NOTICE %s :%s\n" % (nick, msg))
    
def getNick(msg): # Returns the nickname of whoever requested a command from a RAW irc privmsg. Example in commentary below.
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split('!')[0].replace(':','')

def getUser(msg): # Returns the user and host of whoever requested a command from a RAW irc privmsg. Example in commentary below.
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split(" PRIVMSG ")[0].translate(None, ':')

def getChannel(msg): # Returns the channel from whereever a command was requested from a RAW irc PRIVMSG. Example in commentary below.
  # ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
  return msg.split(" PRIVMSG ")[-1].split(' :')[0]

def joinChan(chan): # This function is used to join channels.
  ircsock.send("JOIN %s\n" % (chan))

def joinChans(chans): # This is used to join all the channels in the array 'chans'
  for i in chans:
    ircsock.send("JOIN %s\n" % (i))

def hello(msg): # This function responds to a user that inputs "Hello botxxy"
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    chan = getChannel(msg)
    myprint("%s said hi in %s" % (nick, chan))
    sendChanMsg(chan, "Hello %s! Type !help for more information." % (nick))
  
def identify(again):
  ircsock.send("NICK %s\n" % (botnick)) # Here we actually assign the nick to the bot
  time.sleep(3)
  ircsock.send("NICKSERV IDENTIFY %s\n" % (botpassword)) # Identifies the bot's nickname with nickserv
  myprint("Bot identified")
  if again:
    joinChans(chans)
    
def resetLog():
  with open("botlog.log", "w") as f:
    f.write('')
    f.close
  myprint("Log reset!")

#========================END OF BASIC FUNCTIONS=====================

#========================INITIALIZATIONS============================

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
  try:
    lines = [line.strip() for line in open('lfm.txt', 'r')]
    API_KEY = lines[0]
    API_SEC = lines[1]
    global lastfm
    lastfm = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SEC, username = '', password_hash = '')
    myprint("last.fm API -> Loaded")
  except IOError as e:
    myprint("last.fm API -> FAIL | %s" % e)
    

# 4chan board list

def loadValidBoards():
  global validBoards
  validBoards = s4chan.getValidBoards()
  myprint("Valid boards -> %s" % validBoards)

#========================END OF INITIALIZATIONS=====================

          #AUTHENTICATION

def authCmd(msg): # Authenticates a nick with the bot
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
      password = msg.split("!pass")[1].lstrip(' ') # RAW password
      if not password:
        sendNickMsg(nick, "Bad arguments. Usage: !pass <password>")
      else:
        password = hashlib.sha256(password).hexdigest() # A HEX representation of the SHA-256 encrypted password
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

          #INVITE

def inviteCmd(msg): # Parses the message to extract NICK and CHANNEL
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
      if not target: # Checks if user inserted a nickname to invite
        sendChanMsg(chan, "Bad arguments. Usage: !invite <nick>")
      else: # Success
        myprint("Inviting %s to channel %s" % (target, chan))
        sendChanMsg(chan, "Inviting %s here..." % (target))
        invite(target, chan)
  
def invite(nick, chan): # Invites given nickname to present channel
  ircsock.send("INVITE %s %s\n" % (nick, chan))

          #VOICE

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
      if not target: # Checks if user inserted a nickname to voice
        sendChanMsg(chan, "Bad arguments. Usage: !voice <nick>")
      else: # Success
        myprint("Voicing %s on channel %s" % (target, chan))
        voice(target, chan)

def voice(nick, chan):
  ircsock.send("MODE %s +v %s\n" % (chan, nick))

          #DEVOICE

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
      if not target: # Checks if user inserted a nickname to devoice
        sendChanMsg(chan, "Bad arguments. Usage: !devoice <nick>")
      elif target != botnick: # Success
        myprint("Devoicing %s on channel %s" % (target, chan))
        devoice(target, chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")

def devoice(nick, chan):
  ircsock.send("MODE %s -v %s\n" % (chan, nick))

          #OP

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
      if not target: # Checks if user inserted a nickname to op
        sendChanMsg(chan, "Bad arguments. Usage: !op <nick>")
      else: # Success
        myprint("Giving op to %s on channel %s" % (target, chan))
        op(target, chan)

def op(nick, chan):
  ircsock.send("MODE %s +o %s\n" % (chan, nick))

          #DEOP

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
      if not target: # Checks if user inserted a nickname to deop
        sendChanMsg(chan, "Bad arguments. Usage: !deop <nick>")
      elif target != botnick: # Success
        myprint("Taking op from %s on channel %s" % (target, chan))
        deop(target, chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")

def deop(nick, chan):
  ircsock.send("MODE %s -o %s\n" % (chan, nick))

          #HOP

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
      if not target: # Checks if user inserted a nickname to hop
        sendChanMsg(chan, "Bad arguments. Usage: !hop <nick>")
      else: # Success
        myprint("Giving hop to %s on channel %s" % (target, chan))
        hop(target, chan)

def hop(nick, chan):
  ircsock.send("MODE %s +h %s\n" % (chan, nick))

          #DEHOP

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
      if not target: # Checks if user inserted a nickname to dehop
        sendChanMsg(chan, "Bad arguments. Usage: !dehop <nick>")
      elif target != botnick: # Success
        myprint("Taking hop from %s on channel %s" % (target, chan))
        dehop(target, chan)
      else:
        sendChanMsg(chan, "Don't you dare make me demote myself.")

def dehop(nick, chan):
  ircsock.send("MODE %s -h %s\n" % (chan, nick))

          #TOPIC

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

          #KICK

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
      if not target: # Checks if user inserted a nickname to kick
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

          #RANDOM KICK

def randKick(nicks, chan):
  size = len(nicks) - 1 # Correcting offset (this means if we have an array with 5 elements we should pick a random number between 0 and 4)
  rand = random.randint(0, size) # Picks a random number
  if botnick not in nicks[rand]: # Prevents bot from being kicked by !randkick
    myprint("Randomly kicking %s from %s" % (nicks[rand], chan))
    kick (nicks[rand], chan, 1)
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

          #DICE

def dice(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    chan = getChannel(msg)
    dice = random.randint(1,6) # converts the integer dice to a string to be concatenated in the final output
    myprint("%s rolled the dice and got a %d" % (nick, dice))
    sendChanMsg(chan, "%s rolled a %d" % (nick, dice))

          #QUOTES

def quoteCmd(msg): #TODO: quote IDs
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
        author = line.split ("|!|")[0]
        quote = line.split ("|!|")[1]
        myprint("%s | %s" % (author, quote)) #debugging
        sendChanMsg(chan, "[Quote] %s" % (quote))
      else:
        myprint("File quotes.txt is empty")
        sendChanMsg(chan, "There are no quotes on the DB. Could something be wrong???")

def addQuote(msg):
  nick = getNick(msg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]: # Checks if quote was sent outside of a channel
      myprint("%s sent !addquote outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      # ":b0nk!LoC@fake.dimension PRIVMSG #test :!quote random"
      newQuote = msg.split("!addquote")[1].lstrip(' ')
      if not newQuote: # Checks for empty quote
        sendChanMsg(chan,"Bad arguments. Usage: !addquote [<quote>]")
      else:
        global quotes
        quotes.append(nick + "|!|" + newQuote)
        myprint("%s added '%s'" % (nick, newQuote))
        with open("quotes.txt", 'w') as f:
          for i in quotes:
            f.write("%s\n" % i)
        f.closed
        sendChanMsg(chan, "Quote added!")

          #BLUEBERRYFOX

def bbfquotes(msg): # blueberryfox's private function
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !blueberry outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      myprint("Sending blueberryfox's fav quotes to %s" % (chan))
      sendChanMsg (chan, "Blueberryfoxes favorite Quotes: One, two, three, four, I declare a thumb war, five, six, seven, eight I use this hand to masturbate")
      time.sleep(1)
      sendChanMsg (chan, "I was like ohho!")
      time.sleep(1)
      sendChanMsg (chan, "I love your hair")

          #GREET MESSAGES

def setGreetCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' in msg.split(':')[1]: #let's make sure people use this privately so that people won't see the welcoming message until they join a channel
      chan = getChannel(msg)
      myprint("%s sent !setjoinmsg in %s. Sending warning..." % (nick, chan))
      sendChanMsg(chan, "Don't do that in the channel %s" % (nick))
      sendNickMsg(nick, "Send it as a notice or query(pvt)")
    else:
      newMsg = msg.split(":!setjoinmsg")[1].lstrip(' ') # Retrieves the entry message
      if not newMsg: # Checks if entry message is empty
        setGreet(nick, newMsg, False) # if empty we send False to setGreet so the bot knows the user wants to unset his greet
      else:
        setGreet(nick, newMsg, True) # in this case the user wants to change or create an entry message so we send True

def setGreet(nick, newMsg, toSet):
  global greets
  changed = False
  for idx, content in enumerate(greets): # Here we start scanning the array
    if nick + "|!|" in str(content): # In this case the user already has a greet message
      if toSet: # This will happen if there is a new entry message and not an empty one
        greets[idx] = nick + "|!|" + newMsg # Changes the entry message to the new one
        myprint("Resetting %s's greet message to '%s'" % (nick, newMsg))
        sendNickMsg(nick, "Entry message re-set!")
        changed = True
        break # We've found the nickname we can get out of the loop
      else: # This will happen if there is an empty entry message on an existing nick
        greets[idx] = None # Completely erases the content
        greets.remove(None)
        myprint("Unsetting %s's greet message" % (nick))
        sendNickMsg(nick, "Entry message unset!")
        changed = True
        break # We've found the nickname we can get out of the loop
  if toSet and not changed: # this will happen if there is a message and we didn't find a nickname in the file which means it's the 1st time being used or it was erased previously
        greets.append(nick + "|!|" + newMsg) # Adds the nick and corresponding greet message
        myprint("Setting %s's greet message to '%s'" % (nick, newMsg))
        sendNickMsg(nick, "Entry message set!")
  with open("greet.txt", 'w') as f:
    for i in greets:
      f.write("%s\n" % i)
  f.closed # Closes the file to save resources
  
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

  
          #TAG (play catch)
          
def startTag(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]: # Checks of command was sent in a channel
      myprint("%s sent !starttag outside of a channel" % (nick)) #debugging
      sendNickMsg(nick, "You are not in a channel") # Warned the nickname
    else:
      global isTagOn, tagged, taggers
      taggers.remove(botnick)
      if 'ChanServ' in taggers:
        taggers.remove('ChanServ')
      chan = getChannel(msg) # Get the channel where the game is taking place
      if not isTagOn: # Checks if a game is in progress
        tagged = nick # Whoever starts the game is it
        isTagOn = True # Set game start
        sendChanMsg(chan, "The game starts and %s is it!" % (nick))
      else: # Warns if game is on progress
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
        if not target: # Checks if the nick tagged nothing
          sendChanMsg(chan, "Tag who??? Usage: !tag <nick>")
        else:
          target = target.rstrip(' ') # Removes trailing spaces left by some clients auto-complete
          if target is botnick: # Checks if the bot gets tagged
            myprint("%s tagged the bot!" % (nick))
            sendChanMsg(chan, "%s tagged me!" % (nick))
            target = random.choice(taggers) # Bot picks a random player to tag
            myprint("Tagging %s..." % (target))
            tagged = target
            sendChanMsg(chan, "%s Tag! You're it!" % (target))
            prevTagged = nick
          elif target in taggers: # Target must exist in the list of players
            if nick == tagged: # Checks if the player is it
              if nick == target: # Checks if player is tagging himself
                myprint("%s tagged himself" % (nick))
                sendChanMsg(chan, "Don't tag yourself %s" % (nick))
              else: # Player tags someone other than himself or the bot
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
        if not target: # Checks if the nick wrote anything to set
          sendChanMsg(chan, "Set who??? Usage: !settagged <nick>")
        else:
          target = target.rstrip(' ') # Removes trailing spaces left by some clients auto-complete
          if target in taggers: # Target must exist in the list of players
            if nick == prevTagged:
              if nick == target:
                myprint("%s set himself as tagged" % (nick))
                sendChanMsg(chan, "Don't tag yourself %s" % (nick))
              elif target == botnick:
                myprint("%s set the bot as tagged!" % (nick))
                sendChanMsg(chan, "%s tagged me instead!" % (nick))
                target = random.choice(taggers) # Bot picks a random player to tag
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
      
          #ROSE
          
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
      if not target: # Checks for a target to send a rose to
        sendChanMsg(chan, "%s don't keep the roses to yourself. Usage: !rose <nick>" % (nick))
      else:
        target = target.rstrip(' ')
        if nick == target: # Checks if nick is sending a rose to himself
          myprint("%s is being selfish with the roses" % (nick))
          sendChanMsg(chan, "Don't be selfish %s give that rose someone else" % (nick))
        elif target == botnick:
          myprint("%s sent a rose to the bot." % (nick))
          sendChanMsg(chan, "%s gave me a rose!" % (nick))
          sendChanMsg(chan, "[%s] %s [%s]" % (nick, rosestr, target))
          sendChanMsg(chan, ":3 thanks 4<3")
        else: # Success (normal case)
          myprint("%s sent a rose to %s" % (nick, target))
          sendChanMsg(chan, "%s gives a rose to %s" % (nick, target))
          sendChanMsg(chan, "[%s] %s [%s]" % (nick, rosestr, target))


          #CAKE

'''
  this function actually prints the cake, since it's a multi-line
  ascii art thing and i didn't want to rewrite its code everywhere
'''
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
      if not target: # Checks for a target to promise some cake
        sendChanMsg(chan, "%s, there is science to do. Usage: !cake <nick>" % (nick))
      else:
        target = target.rstrip(' ')
        if nick == target: # Checks if nick is eating the cake by himself
          myprint("%s is tricking test subjects and eating the cake" % (nick))
          sendChanMsg(chan, "Those test subjects won't test for free! %s, leave some cake for them" % (nick))
        elif target == botnick:
          myprint("%s gives some tasty cake to the bot." % (nick))
          printCake(chan)
          sendChanMsg(chan, "Thank you %s!" % (nick))
          sendChanMsg(chan, "It's so delicious and moist.")
        else: # Success (normal case)
          myprint("%s is sharing some cake" % (nick))
          if random.randint(1,100) > 95:
            sendChanMsg(chan, "%s gives some tasty cake to %s" % (nick, target))
            printCake(chan)
          else:
            sendChanMsg(chan, "Unfortunately, %s %s" % (target, random.choice(cakeDeaths)))
        
          #BOOBS
          
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
      if not target: # Checks for a target to show boobs to
        sendChanMsg(chan, "%s don't hide those boobs. Usage: !boobs <nick>" % (nick))
      else:
        target = target.rstrip(' ')
        if nick == target: # Checks if nick is sending !boobs to itself
          myprint("%s is being shy with those boobs" % (nick))
          sendChanMsg(chan, "Stop looking at the mirror %s show us them boobs" % (nick))
        elif target == botnick:
          myprint("%s sent !boobs to the bot." % (nick))
          sendChanMsg(chan, "%s those are cute" % (nick))
          sendChanMsg(chan, "But mine are bigger --> ( . Y . )")
        else: # Success (normal case)
          myprint("%s sent !boobs to %s" % (nick, target))
          sendChanMsg(chan, "%s shows %s some boobs" % (nick, target))
          sendChanMsg(chan, "[%s] %s [%s]" % (nick, boobsstr, target))
        
          #SAY
          
def sayCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' in msg.split(':')[1]:
      chan = getChannel(msg)
      myprint("%s sent !say in %s. Sending warning..." % (nick, chan))
      sendChanMsg(chan, "Don't do that in the channel %s" % (nick))
      sendNickMsg(nick, "Send it as a notice or query(pvt)")
    else: # ":b0nk!~LoC@fake.dimension PRIVMSG botxxy :!say #boxxy lol message"
      target = msg.split(':')[2].split(' ')[1]
      message = msg.split(target)[1].lstrip(' ')
      ircsock.send("PRIVMSG %s :%s\n" % (target, message))
    
          #8BALL
          
def eightBallCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !8ball outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      question = msg.split(':!8ball')[1].lstrip(' ')
      if not question or '?' not in question:
        myprint("%s didn't ask a question" % (nick))
        sendChanMsg(chan, "How about you ask me a question properly %s? Usage: !8ball [<question>]?" % (nick))
      else:
        global eightball
        answer = random.choice(eightball)
        if answer:
          myprint("8ball says: %s" % (answer))
          sendChanMsg(chan, "%s asked [%s] the 8ball says: %s" % (nick, question, answer))
        else:
          myprint("No 8ball answers")
          sendChanMsg(chan, "No 8ball answers :(")
        
          #LAST.FM
          
def getLfmUser(nick): # this looks for the last.fm username by nick
  global lfmUsers
  user = ''
  for i in lfmUsers:
    if nick in i:
      user = i.split('|!|')[1]
  return user #returns empty if not found


def setLfmUserCmd(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    lfm_username = msg.split(":.setuser")[1].lstrip(' ')
    if not lfm_username:
      setLfmUser(nick, lfm_username, False) #sends false flag to unset username
    else:
      setLfmUser(nick, lfm_username, True) #sends true flag to set/re-set username


def setLfmUser(nick, lfm_username, toSet):
  global lfmUsers
  changed = False # hit detection
  for idx, content in enumerate(lfmUsers): # scans array
    if nick + "|!|" in str(content): # finds the nickname
      if toSet:
        lfmUsers[idx] = "%s|!|%s" % (nick, lfm_username)
        myprint("%s re-set it's LAST.FM username to %s" % (nick, lfm_username))
        sendNickMsg(nick, "last.fm username re-set!")
        changed = True
        break # get out of loop
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
      f.write('%s\n' % i) # stores data back to file
  f.closed


def compareLfmUsers(msg): # use of the last.fm interface (pylast) in here
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent .compare outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      args = msg.split(':')[2].rstrip(' ').split(' ') # puts usernames in array
      if len(args) == 3: # correct usage
        user1 = args[1] # assigning usernames to vars
        user2 = args[2]
        global lastfm
        try:
          compare = lastfm.get_user(user1).compare_with_user(user2, 5) # comparison information from pylast
          global cmp_bars
          index = round(float(compare[0]), 2)*100 # compare[0] contains a str with a num from 0-1 here we round it to 4 digits and turn it to a percentage 0-100
          if index < 1.0:
            bar = cmp_bars[4]
          else:
            bar = cmp_bars[int(index / 25.01)] # int(index / 25.01) will return an integer from 0 to 3 to choose what bar to show
          raw_artists = []
          raw_artists = compare[1] # compare[1] contains an array of pylast.artist objects
          artist_list = ''
          if len(raw_artists) > 0: # users have artists in common
            while raw_artists:
              artist_list += raw_artists.pop().get_name() + ", " # artist list string is built
            artist_list = artist_list.rstrip(", ")
          else: # no artists in common so we return '(None)'
            artist_list = "(None)"
            myprint("Comparison between %s and %s %d%% %s" % (user1, user2, index, artist_list))
            sendChanMsg(chan, "%s Comparison: %s %s %s - Similarity: %d%% - Common artists: %s" % (lfm_logo, user1, bar, user2, index, artist_list))
        except pylast.WSError as e: # catched the exception, user truly does not exist
          print e.details
          sendChanMsg(chan, "%s Error: %s" % (lfm_logo, e.details))
          return None # GTFO
      else:
        myprint("%s sent bad arguments for .compare" % (nick))
        sendChanMsg(chan, "%s Bad arguments! Usage: .compare <username1> [username2]" % (lfm_logo)) # warning for bad usage


def nowPlaying(msg): # use of the last.fm interface (pylast) in here
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent .np outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      target = msg.split(":.np")[1].lstrip(' ')
      if not target: # let's check the file
        target = getLfmUser(nick)
      if not target: # he is not in the db
        sendChanMsg(chan , "%s First set your username with .setuser <last.fm username>. Alternatively use .np <last.fm username>" % (lfm_logo))
        myprint("%s sent .np but is not registered" % (nick))
      else:
        global lastfm
        try:
          lfm_user = lastfm.get_user(target) # returns pylast.User object
          if lfm_user.get_playcount() < 1: # checks if user has scrobbled anything EVER
            myprint("%s has an empty library" % (target)) # no need to get a nowplaying when the library is empty
            sendChanMsg(chan, "%s %s has an empty library" % (lfm_logo, target))
          else:
            np = lfm_user.get_now_playing() # np is now a pylast.Track object
            if np is None: # user does not have a now listening track
              myprint("%s does not seem to be playing any music right now..." % (target))
              sendChanMsg(chan, "%s %s does not seem to be playing any music right now..." % (lfm_logo, target))
            else: # all went well
              artist_name = np.artist.get_name()# string containing artist name
              track = np.title #string containing track title
              
              try: # here we check if the user has ever played the np track
                playCount = int(np.get_add_info(target).userplaycount)
              except (ValueError, TypeError): #this error means track was never played so we just say it's 1
                playCount = 1
              if playCount == 0:
                playCount = 1

              np = np.get_add_info(target)
              loved = ''
              
              if np.userloved == '1': # checks if np is a loved track to show when brodcasted to channel
                loved = "4<3 "
              
              raw_tags = np.get_top_tags(5)
              if not raw_tags: # some tracks have no tags so we request the artist tags
                raw_tags = np.artist.get_top_tags(5)
              tags = ', '
              while raw_tags:
                tags += raw_tags.pop().item.name + ", " # builds tags string
              tags = tags.rstrip(", ") # removes last comma
              
              myprint("%s is now playing: %s - %s %s(%d plays%s)" % (target, artist_name, track, loved, playCount, tags))
              sendChanMsg(chan, "%s %s is now playing: %s - %s %s(%d plays%s)" % (lfm_logo, target, artist_name, track, loved, playCount, tags))# broadcast to channel
              #last.fm | b0nk is now playing: Joan Jett and the Blackhearts - You Want In, I Want Out (1 plays, rock, rock n roll, Joan Jett, 80s, pop)
        except pylast.WSError as e: # catched the exception, user truly does not exist
          print e.details
          sendChanMsg(chan, "%s Error: %s" % (lfm_logo, e.details))
          return None # GTFO
    

          #TWITTER
          
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


          #FML
          
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


          #URL SPOILER

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
            r, data = h.request(url, "GET", headers = def_headers)
            soup = bs4.BeautifulSoup(data)
            url_title = stripHTML(str(soup.find('title')))
            url_title = unescape(url_title).strip().replace('\n', ' ').rstrip(' - YouTube')
            myprint("Title: %s" % (url_title))
            try:
              yt_link = 'https://youtu.be/%s' % re.search('v\=([a-zA-Z0-9-_=]+)', url).group(1)
              myprint (yt_link)
              sendChanMsg(chan, "%s's link title: %s %s | %s" % (nick, yt_logo, url_title, yt_link))
            except(IndexError):
              r, data = h.request(url, "GET", headers = def_headers)
              soup = bs4.BeautifulSoup(data)
              url_title = stripHTML(str(soup.find('title')))
              url_title = unescape(url_title).strip().replace('\n', ' ')
              myprint("Title: %s" % (url_title))
              sendChanMsg(chan, "%s's link title: %s %s" % (nick, yt_logo, url_title))
          elif re.search("4chan.org/(.+)/res/(\d+)", url):
            threadInfo = re.search("4chan.org/(.+)/res/(\d+)", url)
            board = threadInfo.group(1)
            thread = threadInfo.group(2)
            url_title = s4chan.getThreadInfo(board, thread)
            myprint("4chan Title: %s" % url_title)
            sendChanMsg(chan, "%s's link title: %s" % (nick, url_title))
          else:
            r, data = h.request(url, "GET", headers = def_headers)
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
        
  
          #GOOGLE SEARCH
          
def gSearch(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !google outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      query = msg.split(":!google")[1].lstrip(' ')
      if query:
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
      query = msg.split(":!images")[1].lstrip(' ')
      if query:
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
        
          #4chan search
          
def chanSearch(msg):
  nick = getNick(msg)
  global ignUsrs
  if nick not in ignUsrs:
    if '#' not in msg.split(" PRIVMSG ")[-1].split(' :')[0]:
      myprint("%s sent !4chan outside of a channel" % (nick))
      sendNickMsg(nick, "You are not in a channel")
    else:
      chan = getChannel(msg)
      query = msg.split(":!4chan")[1].strip()
      args = query.split(" ", 1)
      if len(args) is 2:
        board = args[0]
        sterms = args[1]
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


          #Humble Bundle
          
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
      sendChanMsg(chan, "%s" % games)
  
          #QUIT

def quitIRC(): #This kills the bot!
  myprint("Killing the bot...")
  ircsock.send("QUIT :%s\n" % quitmsg)


      #HELP (THE WALL OF TEXT) keep this on the bottom

def helpcmd(msg): #Here is the help message to be sent as a private message to the user
  nick = getNick(ircmsg)
  global ignUsrs, authUsrs
  if nick not in ignUsrs:
    myprint("Help requested by %s" % (nick))
    sendNickMsg(nick, "You have requested help.")
    time.sleep(0.5) # 0.5 seconds to avoid flooding
    sendNickMsg(nick, "You can say 'Hello %s' in a channel and I will respond." % (botnick))
    time.sleep(0.5)
    sendNickMsg(nick, "You can also invite me to a channel and I'll thank you for inviting me there.")
    time.sleep(0.5)
    sendNickMsg(nick, "General commands: !help !invite !rtd !quote !addquote !setjoinmsg !starttag !endtag !tag !rose !boobs !8ball !pass !cake !fml")
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
  ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TODO: IPv6 ???
  ircsock = ssl.wrap_socket(ircsock) # SSL wrapper for the socket
  ircsock.settimeout(250.0)
  ircsock.connect((server, ssl_port)) # Here we connect to the server using the port defined above
  ircsock.send("USER %s %s %s %s\n" % (botuser, bothost, botserver, botname)) # Bot authentication
  time.sleep(3)
  identify(False) # Bot identification
  time.sleep(3)
  joinChans(chans)
  time.sleep(3)
  stack = []
  
  while 1: # This is our infinite loop where we'll wait for commands to show up, the 'break' function will exit the loop and end the program thus killing the bot
    stack.append(ircsock.recv(1024)) # Receive data from the server
    while stack:
      ircmsg = stack.pop()
      ircmsg = ircmsg.strip('\n\r') # Removing any unnecessary linebreaks
      print ircmsg # Here we print what's coming from the server
    
      if "PING :" in ircmsg: # If the server pings us then we've got to respond!
        reply = ircmsg.split("PING :")[1] # In some IRCds it is mandatory to reply to PING the same message we recieve
        ping(reply)
      
      if " 353 " in ircmsg:
        try:
          # ":irc.catiechat.net 353 botxxy = #test :KernelPone ~b0nk CommVenus @botxxy " 
          chan = ircmsg.split(" = ")[1].split(' ')[0]
          ircmsg = ircmsg.split(':')[2] # Returns raw list of nicks
          ircmsg = ircmsg.translate(None, '~@+&%') # Removes user mode characters
          ircmsg = ircmsg.strip() # Removes an annoying SPACE char left by the server at the end of the string
          nicks = ircmsg.split(' ') # Puts nicks in an array
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
      
      if ":hello " + botnick in ircmsg.lower() or ":hi " + botnick in ircmsg.lower(): # If we can find "Hello/Hi botxxy" it will call the function hello(nick)
        hello(ircmsg)
        
      if ":!help" in ircmsg: # checks for !help
        helpcmd(ircmsg)
      
      if ":!ident" in ircmsg:
        user = getUser(ircmsg)
        if user == "b0nk!~LoC@fake.dimension":
          identify(True)
          
      if ":!newlog" in ircmsg:
        user = getUser(ircmsg)
        if user == "b0nk!~LoC@fake.dimension":
          resetLog()
        
      if ":!die" in ircmsg: # checks for !die
        user = getUser(ircmsg)
        if user == "b0nk!~LoC@fake.dimension": # TODO: use auth
          quitIRC()
          sys.exit(0)
        else:
          nick = getNick(ircmsg)
          myprint("%s tried to kill the bot. Sending warning..." % (nick))
          sendNickMsg(nick, "I'm afraid I can't let you do that %s..." % nick)
        
      if ":!reload" in ircmsg: # let's say it was made to reload the vars and arrays
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
        
      if ":!blueberry" in ircmsg: #this will broadcast all of blueberrys favorite quotes :3
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
        
      if hasURL is not None and 'nospoil' not in ircmsg:
        urlSpoiler(ircmsg)
        hasURL = None
    
      if ircmsg.startswith("ERROR :Closing Link:"):
        raise socket.error('derp')
      
except socket.error as e:
  myprint("Bot killed / timedout (%s)" % e)
  sys.exit(-1)

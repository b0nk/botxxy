# Import the necessary libraries.
import socket
import ssl
import time
from mylib import myprint

# Some basic variables used to configure the bot
#
server = "irc.catiechat.net"
# default port
port = 6667
# ssl port
ssl_port = 6697
# default channels
chans = ["#test"]
# bot nick
botnick = "feature-test"
botuser = "tuser"
bothost = "thost"
botserver = "tserver"
botname = "tname"
botpassword = ""


# ============BASIC FUNCTIONS TO MAKE THIS A BIT EASIER===============
# This is our first function! It will respond to server Pings.
def ping(reply):
  # In some IRCds it is mandatory to reply to PING the same message we recieve
  ircsock.send("PONG :%s\n" % (reply))
  # myprint("PONG :%s" % (reply))


def sendChanMsg(chan, msg):
  # This sends a message to the channel 'chan'
  ircsock.send("PRIVMSG %s :%s\n" % (chan, msg.encode("utf8")))


def sendNickMsg(nick, msg):
  # This sends a notice to the nickname 'nick'
  ircsock.send("NOTICE %s :%s\n" % (nick, msg.encode("utf8")))


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
  chan = getChannel(msg)
  myprint("%s said hi in %s" % (nick, chan))
  sendChanMsg(chan, "Hello %s!" % (nick))

# ========================END OF BASIC FUNCTIONS=====================

# Connection
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SSL wrapper for the socket
ircsock = ssl.wrap_socket(ircsock)
# Here we connect to the server using the port defined above
ircsock.connect((server, ssl_port))
time.sleep(2)
# Bot authentication
ircsock.send("USER %s %s %s %s\n" % (botuser, bothost, botserver, botname))
# Here we actually assign the nick to the bot
ircsock.send("NICK %s\n" % (botnick))
time.sleep(2)
joinChans(chans)

# This is our infinite loop where we'll wait for commands to show up, the 'break' function will exit the loop and end the program thus killing the bot
while 1:
  # Receive data from the server
  ircmsg = ircsock.recv(1024)
  # Removing any unnecessary linebreaks
  ircmsg = ircmsg.strip('\n\r')
  # Here we print what's coming from the server
  myprint(ircmsg)

  # If the server pings us then we've got to respond!
  if "PING :" in ircmsg:
    # In some IRCds it is mandatory to reply to PING the same message we recieve
    reply = ircmsg.split("PING :")[1]
    ping(reply)

  # If we can find "Hello botnick" it will call the function hello()
  if ":hello " + botnick in ircmsg.lower():
    hello(ircmsg)

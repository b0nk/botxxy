﻿# https://en.wikipedia.org/wiki/List_of_Internet_Relay_Chat_commands
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python
# http://forum.codecall.net/topic/59608-developing-a-basic-irc-bot-with-python/

# Import the necessary libraries.
import socket
import ssl

# Some basic variables used to configure the bot

server = "boxxybabee.catiechat.net" # EU server
#server = "anewhopeee.catiechat.net" # US server
port = 6667 # default port
ssl_port = 6697 # ssl port
chans = ["#test", "#your_channels_here"] #default channels
botnick = "skeleton" # bot nick
botuser = "botuser"
bothost = "bothost"
botserver = "botserver"
botname = "botname"
botpassword = ""

# Global vars

prompt = '>> '

#============BASIC FUNCTIONS TO MAKE THIS A BIT EASIER===============

def myprint(msg): #USE THIS ISNTEAD OF print
	print "%s%s" % (prompt, msg)
	
def sendChanMsg(chan, msg): # This sends a message to the channel 'chan'
	ircsock.send("PRIVMSG %s :%s\n" % (chan, msg))

def sendNickMsg(nick, msg): # This sends a notice to the nickname 'nick'
	ircsock.send("NOTICE %s :%s\n" % (nick, msg))

def getNick(msg): # Returns the nickname of whoever requested a command from a RAW irc privmsg. Example in commentary below.
	# ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
	return msg.split('!')[0].replace(':','')

def getChannel(msg): # Returns the channel from whereever a command was requested from a RAW irc PRIVMSG. Example in commentary below.
	# ":b0nk!LoC@fake.dimension PRIVMSG #test :lolmessage"
	return msg.split(" PRIVMSG ")[-1].split(' :')[0]

def joinChan(chan): # This function is used to join channels.
	ircsock.send("JOIN %s\n" % (chan))

def joinChans(chans): # This is used to join all the channels in the array 'chans'
	for i in chans:
		ircsock.send("JOIN %s\n" % (i))

#========================END OF BASIC FUNCTIONS=====================

					#PING

def ping(reply): # This is our first function! It will respond to server Pings.
	ircsock.send("PONG :%s\n" % (reply)) # In some IRCds it is mandatory to reply to PING the same message we recieve
	#myprint("PONG :%s" % (reply))

					#HELLO
					
def hello(msg): # This function responds to a user that inputs "Hello testbot"
	nick = getNick(msg)
	chan = getChannel(msg)
	myprint("%s said hi in %s" % (nick, chan))
	sendChanMsg(chan, "Hello %s! Type !help for more information." % (nick))

# Connection

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock = ssl.wrap_socket(ircsock) # SSL wrapper for the socket
ircsock.connect((server, ssl_port)) # Here we connect to the server using the port defined above
ircsock.send("USER %s %s %s %s\n" % (botuser, bothost, botserver, botname)) # Bot authentication
ircsock.send("NICK %s\n" % (botnick) ) # Here we actually assign the nick to the bot
joinChans(chans)

while 1: # This is our infinite loop where we'll wait for commands to show up, the 'break' function will exit the loop and end the program thus killing the bot
	ircmsg = ircsock.recv(4096) # Receive data from the server
	ircmsg = ircmsg.strip('\n\r') # Removing any unnecessary linebreaks
	myprint (ircmsg) # Here we print what's coming from the server
	
	if "PING :" in ircmsg: # If the server pings us then we've got to respond!
		reply = ircmsg.split("PING :")[1] # In some IRCds it is mandatory to reply to PING the same message we recieve
		ping(reply)
	
	if ":hello " + botnick in ircmsg.lower(): # If we can find "Hello botnick" it will call the function hello()
		hello(ircmsg)
	
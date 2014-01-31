"""
Servers.py - Additional Server Thread Thingies
"""

from .util.decorators import command, initializer
from .util.data import get_doc
from threading import Thread
from utils.irc import IRCHandler

@command("server.add", category="multiserver")
def add_new_server(bot, nick, chan, arg):
	server, nick = arg.split()
	config = bot.getconfig().copy()
	config["server"] = server
	config["nick"] = nick
	sbot = bot.__class__(config)
	sbot.manager = bot.manager
	bot.manager.start_bot(sbot)
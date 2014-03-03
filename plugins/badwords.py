from .util.decorators import command

def buildf(x, y):
	def handler(bot, nick, chan, msg):
		if x.lower() in msg.lower():
			y(bot, nick, chan, msg)
	handler.bad_word = x
	return handler

@command('badword', category="policing", re=r"(\S+) is a bad word\.?")
def badword(bot, nick, chan, groups):
	kick_f = lambda b,n,c,m: b._send("KICK %s %s" % (c, n))
	bot.state.events.MessageEvent.register(buildf(groups[0], kick_f))
	bot.msg(chan, "I'll remember that.")

@command('notbad', category="policing")
def notbad(bot, nick, chan, arg):
	for handler in bot.state.events.MessageEvent.handlers:
		if hasattr(handler, "bad_word"):
			if handler.bad_word == arg:
				bot.state.events.MessageEvent.unhandle(handler)
	bot.msg(chan, "Okay!")
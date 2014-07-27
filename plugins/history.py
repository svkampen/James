from .util.decorators import command
from .util.data import get_doc
from itertools import islice

@command('history', category="misc")
def history(bot, nick, chan, arg):
	""" history <n> -> get the last <n> messages said in this channel. """
	if not arg:
		return bot.msg(chan, get_doc())
	arg = int(arg)
	if arg > 50:
		bot.msg(chan, "Sending more than the last 50 messages is not allowed.")

	# get a flattened list of messages
	l = list(bot.state.messages.values())
	flattened_messages = [i for s in l for i in list(islice(s, 0, 128))]

	# now sort the list
	flattened_messages.sort(key=lambda x: x.timestamp, reverse=True)

	msgs = [msg for msg in flattened_messages if msg.channel.name == chan]
	msgs = msgs[:arg]

	for msg in msgs[::-1]:
		bot.msg(nick, str(msg))

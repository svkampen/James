""" Statistics. """

from .util.decorators import command, initializer
from collections import Counter

command_counter = Counter()
seen_args = []

def command_stats(bot, command, args):
	if (not (args in seen_args)) or (not args):
		seen_args.append(args)
		command_counter.update([command.main_hook or command.regex])

@initializer
def initialize_plugin(bot):
	bot.state.events.CommandCalledEvent.register(command_stats)

@command("cstats", category="meta")
def cstats(bot, nick, chan, arg):
	bot.msg(chan, str(command_counter))
"""
Standard functions like quit, part, join, etc.
"""
from .util.decorators import command
import sys


@command('help', category='standard')
def help_me(bot, nick, target, chan, arg):
    if not arg:
        return bot.msg(chan, "commands: %s." % (', '.join(sorted([i for i in bot.cmdhandler.command_names if not i.isdigit()]))))
    return bot.msg(chan, "%s: %s" % (arg, bot.cmdhandler.trigger(arg).function.__doc__.lstrip()))


@command('say', category='standard')
def say(bot, nick, target, chan, arg):
    if not arg:
        return
    bot.msg(chan, arg)


@command('quit', 'exit', category='standard')
def quitbot(bot, nick, target, chan, arg):
    """ Quit the bot. """
    bot.gracefully_terminate()
    sys.exit()


@command('login', category='standard')
def login(bot, nick, target, chan, arg):
    """ Login to the bot. """
    bot.login(nick)


@command('part', category='standard')
def part_channel(bot, nick, target, chan, arg):
    """ Part the specified channel. """
    if not arg:
        arg = chan
    bot.state.rm_channel(arg)


@command('join', category='standard')
def join_channel(bot, nick, target, chan, arg):
    """ Join the specified channel. """
    bot._send("JOIN :%s" % (arg))

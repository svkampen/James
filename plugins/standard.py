""" 
Standard functions like quit, part, join, etc.
"""
from .util.decorators import command, require_admin
import sys

@command('help')
def help_me(bot, nick, chan, arg):
    if not arg:
        return bot.msg(chan, "commands: %s." % (', '.join(bot.cmdhandler.command_names)))
    return bot.msg(chan, "%s: %s" % (arg, bot.cmdhandler.trigger(arg).function.__doc__.lstrip()))
        

@command('quit', 'exit')
def quitbot(bot, nick, chan, arg):
    """ Quit the bot. """
    bot.gracefully_terminate()
    sys.exit()

@command('login')
def login(bot, nick, chan, arg):
    """ Login to the bot. """
    bot.login(nick)

@command('part')
def part_channel(bot, nick, chan, arg):
    """ Part the specified channel. """
    if not arg:
        arg = chan
    bot.state.rm_channel(arg)

@command('join')
def join_channel(bot, nick, chan, arg):
    """ Join the specified channel. """
    bot._send("JOIN :%s" % (arg))

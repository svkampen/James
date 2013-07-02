"""
Elector
"""

from .util.decorators import command
import random


@command('random')
def insult(bot, nick, target, chan, arg):
    """ Pick between a comma separated list of options """
    if not arg:
        return bot.msg(chan, insult.__doc__.strip())

    choices = arg.split(',')
    bot._msg(chan, "%s: %s" % (target, random.choice(choices).strip()))

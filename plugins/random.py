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

    choices = [x.strip() for x in arg.split(',')]
    if choices[-1].startswith('or '):
        choices[-1] = choices[-1][3:]
    bot._msg(chan, "%s: %s" % (target, random.choice(choices)))

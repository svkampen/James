"""
Elector
"""

from .util.decorators import command
import random


@command('random', category='misc')
def elect(bot, nick, chan, arg):
    """ random *args -> Pick between a comma separated list of options """
    if not arg:
        return bot.msg(chan, elect.__doc__.strip())

    choices = [x.strip() for x in arg.split(',')]
    if choices[-1].startswith('or '):
        choices[-1] = choices[-1][3:]
    bot._msg(chan, "%s: %s" % (nick, random.choice(choices)))

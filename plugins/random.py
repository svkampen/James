"""
Elector
"""

from .util.decorators import command
from .util.data import get_doc
import random


@command("random", category="misc")
def elect(bot, nick, chan, arg):
    """ random *args -> Pick between a comma separated list of options """
    if not arg:
        return bot.msg(chan, get_doc())

    choices = [x.strip() for x in arg.split(",")]
    if choices[-1].startswith("or "):
        choices[-1] = choices[-1][3:]
    bot._msg(chan, "%s: %s" % (nick, random.choice(choices)))

"""
Table tennis
"""
from .util.decorators import command

@command('ping')
def urban_lookup(bot, nick, target, chan, arg):
    return bot.msg(chan, "Pong!")

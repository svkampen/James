"""
Table tennis
"""
from .util.decorators import command

@command('ping')
def ping(bot, nick, target, chan, arg):
    return bot.msg(chan, "Pong!")

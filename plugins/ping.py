"""
Socket tennis
"""
from .util.decorators import command

@command('pong')
def pong(bot, nick, target, chan, arg):
    return bot.msg(chan, "Pong!")

@command('pong')
def pong(bot, nick, target, chan, arg):
    return bot.msg(chan, "Ping!")

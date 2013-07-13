"""
Socket tennis
"""
from .util.decorators import command

@command('pong', category='misc')
def pong(bot, nick, target, chan, arg):
    """ Pong """
    return bot.msg(chan, "Pong!")

@command('ping', category='misc')
def ping(bot, nick, target, chan, arg):
    """ Ping """
    return bot.msg(chan, "Ping!")

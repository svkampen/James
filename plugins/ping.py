"""
Socket tennis
"""
from .util.decorators import command

@command('ping', category='misc')
def ping(bot, nick, chan, arg):
    """ Pong """
    return bot.msg(chan, "Pong!")

@command('pong', category='misc')
def pong(bot, nick, chan, arg):
    """ Ping """
    return bot.msg(chan, "Ping!")

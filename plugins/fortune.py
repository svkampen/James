
""" 
Fortune plugin for James.three
"""
from .util.decorators import command
import os

@command('fortune')
def fortune(bot, nick, chan, arg):
    """Get a fortune cookie"""
    cookie = os.popen("fortune -as").read().strip().replace('\t', "    ")
    if cookie:
        if cookie.count("\n") > 5:
            return fortune(bot, nick, chan, arg)
        bot.msg(chan, cookie)

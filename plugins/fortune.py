
"""
Fortune plugin for James.three
"""
from .util.decorators import command
import os


@command('fortune', category='misc')
def fortune(bot, nick, chan, arg):
    """Get a fortune cookie"""
    cookie = os.popen("fortune -as").read().strip().replace('\t', "    ")
    if cookie:
        if cookie.count("\n") > 5:
            return fortune(bot, nick, chan, arg)  # rerun the command, too long of a fortune!
        bot.msg(chan, cookie)

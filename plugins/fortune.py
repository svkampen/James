
""" 
Bash plugin for James.three
"""
from .util.decorators import command
import os

@command('fortune')
def bash(bot, nick, chan, arg):
    """Get a fortune cookie"""
    cookie = os.popen("fortune.sh").read().strip().replaceall("	", "    ")
    if cookie:
        bot.msg(chan, cookie)

""" 
Haha.. eh.. tiny little project here.
"""

from .util.decorators import command
import random
import time
import threading

@command(str(random.randint(0,10000)), short='who')
def whois(bot, nick, target, chan, arg):
    """ Whois a certain user. """
    if not 'is' in arg or \
       len(arg.split(' ', 1)) < 2:
        return # invalid
    arg = arg.split(' is ',1)[1]
    if "?" in arg:
        arg = arg.split("?",1)[0]
    if arg.lower() == 'i':
        arg = nick
    bot.msg('infobot', '!info %s' % (arg))
    WhoisThread(bot, chan).start()

class WhoisThread(threading.Thread):
    def __init__(self, bot, chan):
        super().__init__()
        self.bot = bot
        self.chan = chan
        self.name = "WhoisThread"

    def run(self):
        time.sleep(2.0)
        message = self.bot.state.notices[-1]['message']
        self.bot.msg(self.chan, message) if not 'target' in message else False
        return

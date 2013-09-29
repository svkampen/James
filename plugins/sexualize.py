"""
sexualize.py - a sexualizer
example: exotic -> sexotic
"""

from .util.decorators import initializer
import re

def sexualize(bot, nick, chan, arg):
    if not re.search(r"\bex[-A-Za-z0-9]+\b", arg):
        return
    for word in re.findall(r"\bex[-A-Za-z0-9]+\b", arg):
    	bot.msg(chan, "%s, more like %s" % (word, 's'+word))

@initializer
def initialize_plugin(bot):
    bot.state.events["MessageEvent"].register(sexualize)
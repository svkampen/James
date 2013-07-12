""" 
Dynamically evaluate python code - James.three plugin
"""
from .util.decorators import command, require_admin, initializer
from .util.data import sugar
import functools, code, sys

class IRCterpreter(code.InteractiveConsole):
    def __init__(self, localVars, botinstance):
        self.bot = botinstance
        self.curnick = ""
        self.curchan = ""
        self.cache = []
        code.InteractiveConsole.__init__(self, localVars)

    def write(self, data):
        self.cache.append(data)

    def flushbuf(self):
        out = ''.join(self.cache).rstrip('\n').replace("\n\n", "\n \n")
        if len(out) > 0:
            self.bot.msg(self.curchan, out)
        self.cache = []

    def run(self, nick, chan, code):
        if not 'self' in self.locals.keys():
            self.locals['self'] = self
        self.curnick = nick
        self.curchan = chan
        sys.stdout = sys.interp = self
        self.push(code)
        sys.stdout = sys.__stdout__
        self.flushbuf()

@initializer
def initialize_plugin(bot):
    """ Initialize this plugin. """
    import sys, os, inspect, plugins
    message = lambda x: sys.interp.write("\x01ACTION %s\x01"%(x))
    action = lambda x: sys.interp.write("\x01ACTION %s\x01"%(x))
    bot.state.interp = {'locals':locals()}
    bot.state.interp['locals'].update(globals())

@require_admin
@command('eval', short=">>>")
def eval_it(self, nick, target, chan, arg):
    arg = sugar(arg)
    ip = None
    try:
        ip = self.state.interp[nick.lower()]
    except KeyError:
        lcls = self.state.interp['locals']
        ip = self.state.interp[nick.lower()] = IRCterpreter(lcls, self)
    ip.run(nick, chan, arg)

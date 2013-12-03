""" 
Dynamically evaluate python code - James.three plugin
"""
from .util.decorators import command, require_admin, initializer
from .util.data import sugar, lineify, generate_vulgarity
import code
import sys

class IRCterpreter(code.InteractiveConsole):
    def __init__(self, localVars, botinstance):
        self.bot = botinstance
        self.curnick = ""
        self.curchan = ""
        self.cache = []
        code.InteractiveConsole.__init__(self, localVars)

    def write(self, data):
        self.cache.append(data)

    def is_exception(self, data):
        return True if 'File "<console>", line ' in data else False

    def flushbuf(self):
        out = "".join(self.cache).strip()

        if self.is_exception(out):
            # most likely a traceback, only capture exception
            print(out)
            out = out[out.rfind("\n"):]

        if len(out) > 0:
            for line in lineify(out):
                self.bot.msg(self.curchan, line)
        self.cache = []

    def run(self, nick, chan, code):
        if not "self" in self.locals.keys():
            self.locals["self"] = self
        self.locals["chan"] = chan
        self.locals["nick"] = nick
        self.curnick = nick
        self.curchan = chan
        sys.stdout = sys.interp = self
        self.push(code)
        sys.stdout = sys.__stdout__
        self.flushbuf()

@initializer
def initialize_plugin(bot):
    """ Initialize this plugin. """
    bot.state.data["interp_locals"] = locals()
    bot.state.data["interp_locals"].update(globals())

@require_admin
@command("eval", short=">>>", category="meta")
def eval_it(bot, nick, chan, arg):
    """ eval *args -> Evaluate *args as python code."""
    arg = sugar(arg)
    ip = None
    try:
        ip = bot.state.interp
    except AttributeError:
        lcls = bot.state.data["interp_locals"]
        ip = bot.state.interp = IRCterpreter(lcls, bot)
    ip.run(nick, chan, arg)

@require_admin
@command("flush_eval", short="flush~", category="meta")
def flush_it(bot, nick, chan, arg):
    """ flush -> Flush the eval buffer. """
    ip = bot.state.interp
    ip.cache = []
    bot.msg(chan, "Flushed interpreter buffer.")



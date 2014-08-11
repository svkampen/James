"""
Standard functions like quit, part, join, etc.
"""
from .util.decorators import command, require_admin
import sys
import platform
import time
import inspect
import random
import os
import re
from types import ModuleType, FunctionType
from functools import partial

def get_name(f):
    if type(f) == ModuleType:
        return f.__name__
    elif type(f) == FunctionType:
        return "%s.%s" % (inspect.getmodule(f).__name__, f.__name__)

def command_categories(bot):
    categories = list(bot.cmdhandler.command_help.keys())
    output = "What category do you want? (%s)" % (", ".join(categories))
    return output

@command("rfc", category="misc")
def rfcs(bot, nick, chan, arg):
    """ rfc -> send the two IRC rfcs """
    bot.msg(chan, "http://tools.ietf.org/html/rfc1459.html\nhttp://tools.ietf.org/html/rfc2812.html")

@command("restart", category="standard")
def restart_bot(bot, nick, chan, arg):
    """ restart -> restart the bot """
    bot.gracefully_terminate()
    sys.stdout.flush()
    sys.stderr.flush()
    os.execv("./bot.py", [""])

@command("help", category="standard")
def help_me(bot, nick, chan, arg):
    """ help [command] or [category] -> Get help for a command or category. """
    if not arg:
        return bot.msg(chan, command_categories(bot))
    if arg in bot.cmdhandler.command_help.keys():
        # Is a category, not just a command
        output = "Category %s contains: %s" % (arg,
            ", ".join(bot.cmdhandler.command_help[arg]))
        return bot.msg(chan, output)
    else:
        # Is a command, not a category (or nonexistant)
        if not bot.cmdhandler.trigger(arg):
            return bot.msg(chan,
                "%s: '%s' is a nonexistant command or category!" % (nick, arg))
        else:
            doc = bot.cmdhandler.trigger(arg).function.__doc__.strip()
            bot.msg(chan, "%s: %s" % (nick, doc))

@command("quit", "exit", category="standard")
def quitbot(bot, nick, chan, arg):
    """ quit -> Quit the bot. """
    bot.gracefully_terminate()
    sys.exit()

@require_admin
@command("part", category="standard")
def part_channel(bot, nick, chan, arg):
    """ part <chan> -> Part the specified channel. """
    if not arg:
        arg = chan
    bot._send("PART :%s" % (arg))

@require_admin
@command("join", category="standard")
def join_channel(bot, nick, chan, arg):
    """ join <chan> -> Join the specified channel. """
    if not arg:
        bot.msg(chan, get_doc())
    bot._send("JOIN :%s" % (arg))

@command("version", category="standard")
def version(bot, nick, chan, arg):
    """ version -> return bot/python version information. """ 
    libc_ver = " ".join(platform.libc_ver())
    python_ver = platform.python_version()
    bot_ver = bot.version
    distro = platform.linux_distribution()[0] # "arch" on arch linux
    compiler = platform.python_compiler()

    output = "Bot: %s - Python compiler: %s using %s\n" % (bot_ver, compiler,
        libc_ver)
    output += "Python: %s - Linux distribution: %s" % (python_ver, distro)
    bot.msg(chan, output)


@command("short", category="meta")
def get_shorthook(bot, nick, chan, arg):
    """ short <cmd> -> Get the shorthook for a command, if exists"""
    if not arg:
        return bot.msg(chan, get_doc())
    if bot.cmdhandler.trigger(arg):
        shorthooks = bot.cmdhandler.trigger(arg).short_hooks
        if shorthooks != [] and shorthooks != None:
            return bot.msg(chan, "%s has short hook %s" % (arg, shorthooks[0]))
        else:
            return bot.msg(chan, "%s has no short hook." % (arg))
    else:
        return bot.msg(chan, "%s is not a valid command." % (arg))

@require_admin
@command("plugin.reload", category="meta")
def reload_plugin(bot, nick, chan, arg):
    """ plugin.reload <plugin_name> -> reload a plugin. """
    if not arg:
        return bot.msg(chan, get_doc())
    bot.cmdhandler.reload_plugin(arg)
    bot.msg(chan, "Reloaded plugin %s" % (arg))

@require_admin
@command("plugin.load", category="meta")
def load_plugin(bot, nick, chan, arg):
    """ plugin.load <plugin_name> -> load a plugin """
    if not arg:
        return bot.msg(chan, get_doc())
    try:
        s = bot.cmdhandler.load_plugin(arg)
        if not s:
            bot.msg(chan, "%s: plugin already loaded!" % (nick))
        else:
            bot.msg(chan, "%s: loaded plugin %s" % (nick, s.__name__))
    except ImportError:
        bot.msg(chan, "%s: Nonexistant plugin!" % (nick))

@require_admin
@command("plugin.unload", category="meta")
def unload_plugin(bot, nick, chan, arg):
    """ plugin.unload <plugin_name> -> unload a plugin """
    if not arg:
        return bot.msg(chan, get_doc())
    s = bot.cmdhandler.unload_plugin(arg)
    if not s:
        bot.msg(chan, "%s: plugin not loaded!" % (nick))
    else:
        bot.msg(chan, "%s: unloaded plugin %s" % (nick, arg))


@require_admin
@command("event.disable_handler", category="meta")
def disable_event_handler(bot, nick, chan, arg):
    """ event.disable_handler <event>.<handler.__name__> -> disable handler for event. """
    if not arg:
        bot.msg(chan, get_doc())
    event, handler = arg.split(".")
    e = bot.state.events[event]
    if not e.handlers.disable(handler):
        bot.msg(chan, "Something went wrong while trying to disable %s" % (arg))
    else:
        bot.msg(chan, "Handler %s disabled." % (arg))

@require_admin
@command("event.enable_handler", category="meta")
def enable_event_handler(bot, nick, chan, arg):
    """ event.enable_handler <event>.<handler.__name__> -> enable handler for event. """
    if not arg:
        return bot.msg(chan, get_doc())
    event, handler = arg.split(".")
    e = bot.state.events[event]
    if not e.handlers.enable(handler):
        bot.msg(chan, "Something went wrong while trying to re-enable %s" % (arg))
    else:
        bot.msg(chan, "Handler %s re-enabled." % (arg))
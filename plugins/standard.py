"""
Standard functions like quit, part, join, etc.
"""
from .util.decorators import command, require_admin
import sys
import platform
import time
import inspect
from types import ModuleType, FunctionType

def get_name(f):
    if type(f) == ModuleType:
        return f.__name__
    elif type(f) == FunctionType:
        return "%s.%s" % (inspect.getmodule(f).__name__, f.__name__)

def command_categories(bot):
    categories = list(bot.cmdhandler.command_help.keys())
    output = "What category do you want? (%s)" % (", ".join(categories))
    return output


@command("help", category="standard")
def help_me(bot, nick, chan, arg):
    """ help [command] or [category] -> Get help for a command or category """
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

@command("say", category="standard")
def say(bot, nick, chan, arg):
    """ say *args -> Say *args """
    if not arg:
        return
    bot.msg(chan, arg)


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
    bot._send("JOIN :%s" % (arg))

@command("u.is_identified", category="standard")
def is_identified(bot, nick, chan, arg):
    """ u.is_identified <user> -> Check if user is identified. """
    bot.msg("NickServ", "ACC %s" % (arg))
    time.sleep(4/3)
    is_id = ("3" in bot.state.notices[-1]["message"])
    bot.msg(chan, is_id)

@command("version", category="standard")
def version(bot, nick, chan, arg):
    """ version -> return bot/python version information """ 
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
        return bot.msg(chan, "Usage: short <command>")
    if bot.cmdhandler.trigger(arg):
        shorthooks = bot.cmdhandler.trigger(arg).short_hooks
        if shorthooks != [] and shorthooks != None:
            return bot.msg(chan, "%s has short hook %s" % (arg, shorthooks[0]))
        else:
            return bot.msg(chan, "%s has no short hook." % (arg))
    else:
        return bot.msg(chan, "%s is not a valid command." % (arg))

@command("req.admin?", category="meta")
def is_command_admin(bot, nick, chan, arg):
    """ req.admin? <cmd> -> Check whether a command requires admin privileges """
    if not arg:
        return bot.msg(chan, "Usage: admin? <command>")
    command = bot.cmdhandler.trigger(arg)
    if not command:
        return bot.msg(chan, "Non-existant command!")
    f = command.function
    if hasattr(f, "_require_admin"):
        return bot.msg(chan, "Command %s requires admin privileges." % (arg))
    bot.msg(chan, "Command %s does not require admin privileges." % (arg))

@require_admin
@command("req.admin!", category="meta")
def set_command_admin(bot, nick, chan, arg):
    """ req.admin! <cmd> -> Make a command require admin privileges """
    if not arg:
        return bot.msg(chan, "Usage: req.admin! <command>")
    if not bot.cmdhandler.trigger(arg):
        return bot.msg(chan, "%s: '%s' is a nonexistant command!" % (nick, arg))
    bot.cmdhandler.trigger(arg).function._require_admin = True
    return bot.msg(chan, "%s: '%s' now requires admin privileges" % (nick, arg))

@require_admin
@command("req.admin-", category="meta")
def remove_cmd_admin(bot, nick, chan, arg):
    """ req.admin- <cmd> -> Make a command not require admin privileges """
    if not arg:
        return bot.msg(chan, remove_cmd_admin.__doc__)
    if not bot.cmdhandler.trigger(arg):
        return bot.msg(chan, "%s: '%s' is a nonexistant command" % (nick, arg))
    delattr(bot.cmdhandler.trigger(arg).function, "_require_admin")
    return bot.msg(chan, "%s: '%s' does not require admin privileges anymore" % (nick, arg))

@require_admin
@command("map", category="beta")
def map_command_to(bot, nick, chan, arg):
    """ map <cmd>-><newcmd> -> map a command to another command name """
    args = arg.split("->")
    orig, new = args
    orig_cmd = bot.cmdhandler.trigger(orig)
    orig_cmd.hooks.append(new)
    return bot.msg(chan, "%s: '%s' now has hooks %r" % (nick, orig, orig_cmd.hooks))

@require_admin
@command("cmd.disabled!", category="meta")
def disable_command(bot, nick, chan, arg):
    """ cmd.disabled! <cmd> -> disable a command in the current channel """
    c = bot.state.channels[chan]
    cmd = bot.cmdhandler.trigger(arg).function
    cmd = get_name(cmd)
    c.disabled_commands.add(cmd)
    bot.msg(chan, "Disabled command %s (%s) in channel %s" % (arg, cmd, c))

@require_admin
@command("cmd.disabled?", category="meta")
def is_command_disabled(bot, nick, chan, arg):
    """ cmd.disabled? <cmd> -> check if a command is disabled in the current channel """
    c = bot.state.channels[chan]
    cmd = bot.cmdhandler.trigger(arg).function
    cmd = get_name(cmd)
    if cmd in c.disabled_commands:
        return bot.msg(chan, "Command %s (%s) is disabled in channel %s" % (arg, cmd, c))
    return bot.msg(chan, "Command %s (%s) is not disabled in channel %s" % (arg, cmd, c))

@require_admin
@command("cmd.disabled-", category="meta")
def enable_command(bot, nick, chan, arg):
    """ cmd.disabled- <cmd> -> enable command in the current channel """
    c = bot.state.channels[chan]
    cmd = bot.cmdhandler.trigger(arg).function
    cmd = get_name(cmd)
    c.disabled_commands.discard(cmd)
    bot.msg(chan, "Command %s (%s) is enabled in channel %s" % (arg, cmd, c))

@command("cmd.disabled", category="meta")
def disabled_commands(bot, nick, chan, arg):
    """ cmd.disabled -> show all disabled commands for current channel """
    c = bot.state.channels[chan]
    if c.disabled_commands:
        return bot.msg(chan, "Disabled commands: %s" % (', '.join(c.disabled_commands)))
    bot.msg(chan, "No disabled commands in channel %s" % (c))

@require_admin
@command("plugin.reload", category="meta")
def reload_plugin(bot, nick, chan, arg):
    """ plugin.reload <plugin_name> -> reload a plugin """
    if not arg:
        return bot.msg(chan, reload_plugin.__doc__.strip())
    bot.cmdhandler.reload_plugin(arg)
    bot.msg(chan, "Reloaded plugin %s" % (arg))

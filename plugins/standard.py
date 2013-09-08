"""
Standard functions like quit, part, join, etc.
"""
from .util.decorators import command, require_admin
import sys
import platform

def command_categories(bot):
    categories = list(bot.cmdhandler.command_help.keys())
    output = "What category do you want? (%s)" % (', '.join(categories))
    return output


@command('help', category='standard')
def help_me(bot, nick, chan, arg):
    """ help [command] or [category] -> Get help for a command or category """
    if not arg:
        return bot.msg(chan, command_categories(bot))
    if arg in bot.cmdhandler.command_help.keys():
        # Is a category, not just a command
        output = "Category %s contains: %s" % (arg,
            ', '.join(bot.cmdhandler.command_help[arg]))
        return bot.msg(chan, output)
    else:
        # Is a command, not a category (or nonexistant)
        if not bot.cmdhandler.trigger(arg):
            return bot.msg(chan,
                "%s: '%s' is a nonexistant command or category!" % (nick, arg))
        else:
            doc = bot.cmdhandler.trigger(arg).function.__doc__.strip()
            bot.msg(chan, "%s: %s" % (nick, doc))

@command('say', category='standard')
def say(bot, nick, chan, arg):
    """ say *args -> Say *args """
    if not arg:
        return
    bot.msg(chan, arg)


@command('quit', 'exit', category='standard')
def quitbot(bot, nick, chan, arg):
    """ quit -> Quit the bot. """
    bot.gracefully_terminate()
    sys.exit()


@command('part', category='standard')
def part_channel(bot, nick, chan, arg):
    """ part <chan> -> Part the specified channel. """
    if not arg:
        arg = chan
    bot.state.rm_channel(arg)


@command('join', category='standard')
def join_channel(bot, nick, chan, arg):
    """ join <chan> -> Join the specified channel. """
    bot._send("JOIN :%s" % (arg))


@command('version', category='standard')
def version(bot, nick, chan, arg):
    """ version -> return bot/python version information """ 
    libc_ver = ' '.join(platform.libc_ver())
    python_ver = platform.python_version()
    bot_ver = bot.version
    distro = platform.linux_distribution()[0] # 'arch' on arch linux
    compiler = platform.python_compiler()

    output = 'Bot: %s - Python compiler: %s using %s\n' % (bot_ver, compiler,
        libc_ver)
    output += 'Python: %s - Linux distribution: %s' % (python_ver, distro)
    bot.msg(chan, output)


@command('short', category='meta')
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

@command('req.admin?', category='meta')
def is_command_admin(bot, nick, chan, arg):
    """ req.admin? <cmd> -> Check whether a command requires admin privileges """
    if not arg:
        return bot.msg(chan, "Usage: admin? <command>")
    command = bot.cmdhandler.trigger(arg)
    if not command:
        return bot.msg(chan, "Non-existant command!")
    f = command.function
    if hasattr(f, '_require_admin'):
        return bot.msg(chan, "Command %s requires admin privileges." % (arg))
    bot.msg(chan, "Command %s does not require admin privileges." % (arg))

@require_admin
@command('req.admin!', category='meta')
def set_command_admin(bot, nick, chan, arg):
    """ req.admin! <cmd> -> Make a command require admin privileges """
    if not arg:
        return bot.msg(chan, "Usage: req.admin! <command>")
    if not bot.cmdhandler.trigger(arg):
        return bot.msg(chan, "%s: '%s' is a nonexistant command!" % (nick, arg))
    bot.cmdhandler.trigger(arg).function._require_admin = True
    return bot.msg(chan, "%s: '%s' now requires admin privileges" % (nick, arg))

@require_admin
@command('map', category='beta')
def map_command_to(bot, nick, chan, arg):
    """ map <cmd>-><newcmd>
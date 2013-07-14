"""
Standard functions like quit, part, join, etc.
"""
from .util.decorators import command
import sys

def command_categories(bot):
    categories = list(bot.cmdhandler.command_help.keys())
    output = "What category do you want? (%s)" % (', '.join(categories))
    return output


@command('help', category='standard')
def help_me(bot, nick, chan, arg):
    """ Get help for a command or category """
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
            bot.msg(chan, "%s: %s -> %s" % (nick, arg, doc))

@command('say', category='standard')
def say(bot, nick, chan, arg):
    """ Say something """
    if not arg:
        return
    bot.msg(chan, arg)


@command('quit', 'exit', category='standard')
def quitbot(bot, nick, chan, arg):
    """ Quit the bot. """
    bot.gracefully_terminate()
    sys.exit()


@command('login', category='standard')
def login(bot, nick, chan, arg):
    """ Login to the bot. """
    bot.login(nick)


@command('part', category='standard')
def part_channel(bot, nick, chan, arg):
    """ Part the specified channel. """
    if not arg:
        arg = chan
    bot.state.rm_channel(arg)


@command('join', category='standard')
def join_channel(bot, nick, chan, arg):
    """ Join the specified channel. """
    bot._send("JOIN :%s" % (arg))


@command('short', category='meta')
def get_shorthook(bot, nick, chan, arg):
    """ Get the short hook for a command (if exists) """
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

from .util.box import twocol
from .util.decorators import command

@command("plugins")
def show_plugins(bot, nick, chan, arg):
    bot.msg(chan, twocol(bot.cmdhandler.loaded_plugins))

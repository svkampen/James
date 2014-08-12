from .util.box import col, box
from .util.decorators import command, initializer

@initializer
def plugin_init(bot):
    bot.state.data["plug_cols"] = 2

@command("plugins")
def show_plugins(bot, nick, chan, arg):
    """ plugins -> print the number of plugins currently loaded. """
    plugins = len(bot.cmdhandler.loaded_plugins)
    out =  bot.hicolor("Module Manager" + box["vert"])
    out += bot.style.color(" %d plugins loaded" % (plugins), color="silver")
    bot.msg(chan, out)

@command("plugins.list")
def list_plugins(bot, nick, chan, arg):
    """ plugins.list -> print a neatly formatted table of plugins. """
    bot.msg(chan, col(bot.cmdhandler.loaded_plugins, bot.state.data["plug_cols"]))

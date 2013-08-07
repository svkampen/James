"""
History
"""
from .util.decorators import command


@command('history', category='meta')
def history(bot, nick, chan, arg):
    """ Get user's history. """
    args = arg.split()
    try:
        if arg.strip().isdigit():
            return bot.msg(target, "\n".join(reversed(list(bot.lastmsgof[chan]['*all'])[0:int(arg.strip())])))
        if len(args) > 2 or len(args) < 2 or int(args[1]) > 16 or int(args[1]) < 1:
            raise Exception("BadUsage")
        victim = args[0].lower()
        bot.msg(target, "\n".join(reversed(["<" + victim + "> " + x for x in bot.lastmsgof[chan][victim]][0:int(args[1])])))
    except:
        bot.msg(chan, "Usage: +history <nick> <1-16> | +history <1-64>")

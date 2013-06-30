"""
History
"""
from .util.decorators import command


@command('history')
def history(bot, nick, target, chan, arg):
    """ Get user's history. """
    args = arg.split()
    try:
        if len(args) > 2 or len(args) < 2 or int(args[1]) > 16 or int(args[1]) < 1:
            return bot.msg(chan, "Usage: +history <nick> <1-16>")
        victim = args[0]
        num = int(args[1])
        bot.msg(chan, "\n".join(reversed(["<" + victim + "> " + x for x in bot.lastmsgof[chan][victim]][0:num])))
    except:
        bot.msg(chan, "Usage: +history <nick> <number>")

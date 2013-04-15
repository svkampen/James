from util.decorators import command
import sys

@command('quit', 'exit')
def quitbot(bot, nick, chan, arg):
    bot.gracefully_terminate()
    sys.exit()

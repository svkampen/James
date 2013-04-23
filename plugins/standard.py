from util.decorators import command
import sys

@command('quit', 'exit')
def quitbot(bot, nick, chan, arg):
    bot.gracefully_terminate()
    sys.exit()

@command('login')
def login(bot, nick, chan, arg):
    bot.login(nick)

@command('part')
def part_channel(bot, nick, chan, arg):
    if not arg:
        arg = chan
    bot.state.rm_channel(arg)

@command('join')
def join_channel(bot, nick, chan, arg):
    bot._send("JOIN :%s" % (arg))

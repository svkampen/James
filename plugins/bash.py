from util.decorators import command
import os

@command('bash', short='$')
def bash(bot, nick, chan, arg):
    """Execute a bash command"""
    return bot._msg(chan, os.popen(arg).read())

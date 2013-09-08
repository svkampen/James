"""
Bash plugin for James.three
"""
from .util.decorators import command, require_admin
import os


@require_admin
@command('bash', short='$', category='programming')
def bash(bot, nick, chan, arg):
    """bash <command> -> Execute a bash command"""
    data = os.popen("""%s""" % (arg)).read().rstrip()
    if data:
        bot.msg(chan, nick + ": " + data)

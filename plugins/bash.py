from .util.decorators import command, require_admin
import os

@require_admin
@command('bash', short='$')
def bash(bot, nick, chan, arg):
    """Execute a bash command"""
    return bot._msg(chan, os.popen("""%s""" % (arg)).read())

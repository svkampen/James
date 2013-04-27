""" 
Bash plugin for James.three
"""
from .util.decorators import command, require_admin
import os

@require_admin
@command('bash', short='$')
def bash(bot, nick, chan, arg):
    """Execute a bash command"""
    return bot.msg(chan, nick+": "+os.popen("""%s""" % (arg)).read())

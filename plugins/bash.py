"""
Bash plugin for James.three
"""
from .util.decorators import command, require_admin
import os


@require_admin
@command('bash', short='$', category='programming')
def bash(bot, nick, chan, arg):
    """Execute a bash command - bash <command>"""
    data = os.popen("""%s""" % (arg)).read().rstrip()
    if data:
        bot.msg(chan, nick + ": " + data)

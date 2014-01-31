"""
Bash plugin for James.three
"""
from .util.decorators import command, require_admin
from .util.data import get_doc
import os

@require_admin
@command("bash", short="$", category="programming")
def bash(bot, nick, chan, arg):
    """bash <command> -> Execute a bash command"""
    if not arg:
        return bot.msg(chan, get_doc())
    data = os.popen("""%s""" % (arg)).read().rstrip()
    if data:
        bot.msg(chan, data)

"""
Bash plugin for James.three
"""
from .util.decorators import command, require_admin
from .util.data import get_doc
from subprocess import Popen, PIPE, STDOUT
import os

@require_admin
@command("ghci", short="$", category="programming")
def bash(bot, nick, chan, arg):
    """bash <command> -> Execute a bash command"""
    if not arg:
        return bot.msg(chan, get_doc())
    data = os.popen("bash -c '%s'" % (arg)).read().strip()
    if data:
        bot.msg(chan, data)

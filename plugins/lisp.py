"""
Common Lisp interpreter
Carter Hinsley <carterhinsley@gmail.com>
"""
from .util.decorators import command
import os
import subprocess

@command('lisp', category='programming')
def lisp(bot, nick, chan, arg):
    """ lisp *args -> Interpret *args as Common Lisp. """
    if not arg:
        return bot._msg(chan, "Usage: lisp [code]")
    f = open("./temp.lisp", 'w')
    f.write(arg)
    f.close()
    p = subprocess.Popen(
        "clisp ./temp.lisp",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=True
        )
    output = p.stdout.read()
    bot.msg(chan, "%s: %s" % (nick, output.decode('utf-8').strip()))
    os.remove(os.path.abspath("temp.lisp"))

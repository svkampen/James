"""
Common Lisp interpreter
Carter Hinsley <carterhinsley@gmail.com>
"""
from .util.decorators import command
import os
import subprocess

@command('lisp')
def lisp(bot, nick, target, chan, arg):
	""" Interpret a Common Lisp snippet. """
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
	bot._msg(chan, "%s: %s" % (nick, output.decode('utf-8').strip()))
	os.remove(os.path.abspath("temp.lisp"))

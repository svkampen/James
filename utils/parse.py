"""
IRC Parser - parse.py
"""

import inspect
import traceback
import re
import codecs
import subprocess
import sys

#SED_REGEX = re.compile(r"^(?:(\S+)[:,]\s)?(?:(.+?)/)?s/(.+?)/([^/]*)/?([gixs]{0,4})?(?: (.*))?")
SED_REGEX = re.compile(r"^(?:(\S+)[:,]\s)?(?:s|(.+?)/s)/((?:\\/|[^/])+)\/((?:\\/|[^/])*?)/([gixs]{0,4})?")

def parse(msg):
    """ Parse an IRC protocol message """
    if msg.startswith("PING"):
        info = {"method": "PING", "arg": msg.split()[-1]}
    else:
        splitmsg = msg.split(" ", 2)
        info = {"method": splitmsg[1], "host": splitmsg[0][1:], "arg":
                splitmsg[2]}
    return info

def evaluate(self, nick, chan, msg):
    """ Evaluate python code. """
    try:
        output = eval(msg, globals(), locals())
        if output is not None:
            self.leo = output
            if type(self.leo) == tuple:
                self.leo = list(self.leo)
                output = list(output)
            return output
    except (NameError, SyntaxError):
        try:
            exec(msg, globals())
        except:
            try:
                exec(msg, locals())
            except:
                try:
                    exec(msg,globals(),locals())
                except:
                    exec(msg,locals(),globals())


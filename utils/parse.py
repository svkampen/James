"""
IRC Parser - parse.py
"""

import inspect
import traceback
import re
import subprocess

def parse(msg):
    """ blah """
    if msg.startswith("PING"):
        info = {'method': 'PING', 'arg': msg.split()[-1]}
    else:
        splitmsg = msg.split(' ', 2)
        info = {'method': splitmsg[1], 'host': splitmsg[0][1:], 'arg':
                splitmsg[2]}
    return info

def evaluate_expression(self, nick, chan, msg):
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

def check_sed(msg):
    if re.match("^(\w+: )?s/.+/.+(/([gi]?){2})?$", msg):
        return True

def sed_escape(msg):
    msg = msg.replace('(', r"\(")
    msg = msg.replace(")", r"\)")
    while msg.count('/') != 3:
        # not valid, because valid is only 3 slashes (s/a/b/)
        msg = msg[:msg.rfind("/")] # strip
    msg = msg[:msg.rfind("/")+1] # good.
    return msg

def sed(bot, nick, chan, msg):
    try:
        to_sed = bot.lastmsgof[nick]
    except KeyError:
        pass

    msg = sed_escape(msg)

    sed_p = subprocess.Popen(
        "echo %s | sed \"%s\"" % (to_sed, msg),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        close_fds=True
    )

    output = sed_p.stdout.read().decode('utf-8').strip()
    return bot.msg(chan, "%s: %s" % (nick, output))


def inline_python(bot, nick, chan, msg):
    """ Execute inline python """
    pieces_of_python = re.findall("`([^`]+)`", msg)
    if pieces_of_python == []:
        return msg
    for piece in pieces_of_python:
        try:
            msg = msg.replace(piece, str(evaluate_expression(bot, nick, chan, piece)))
        except BaseException:
            traceback.print_exc()
    return msg.replace('`', '')


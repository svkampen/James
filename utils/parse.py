"""
IRC Parser - parse.py
"""

import inspect
import traceback
import re
import subprocess

def parse(msg):
    """ Parse an IRC protocol message """
    if msg.startswith("PING"):
        info = {'method': 'PING', 'arg': msg.split()[-1]}
    else:
        splitmsg = msg.split(' ', 2)
        info = {'method': splitmsg[1], 'host': splitmsg[0][1:], 'arg':
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

###
##
## Sed part
##
###

class Seddable(object):
    def __init__(self, msg):
        message_split = msg.split('/')

        replace = message_split[1]
        by = message_split[2]

        self.message = msg
        self.to_replace = replace
        self.by = by

def get_message(bot, sedregex, nick):
    if not nick in bot.state.messages:
        return ""
    for message in bot.state.messages[nick]:
        if re.search(sedregex, message):
            return message
    return ""

def check_sed(msg):
    """ Check whether a message is a sed request """
    if re.match("^(([a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]*)[:,] )?s/.+/.*(/([gi]?){2})?$", msg):
        return True

def sed(bot, nick, chan, msg):
    """ Perform the actual sedding """
    if re.match("^(([a-z_\-\[\]\\^{}|`][a-z0-9_\-\[\]\\^{}|`]*)[:,] )s/.+/.*(/([gi]?){2})?$", msg):
        # target acquired
        split_msg = msg.split(':')
        nick = split_msg[0]
        msg = split_msg[1].strip()

    sedmsg = Seddable(msg)
    to_sed = get_message(bot, sedmsg.to_replace, nick)

    if not to_sed:
        return

    sedmsg.message = to_sed
    sedded_message = re.sub(sedmsg.to_replace, sedmsg.by, sedmsg.message)
    return bot.msg(chan, "FTFY <%s> %s" % (nick, sedded_message))


###
##
## Inline python
##
###

def inline_python(bot, nick, chan, msg):
    """ Execute inline python """
    pieces_of_python = re.findall("`([^`]+)`", msg)
    if pieces_of_python == []:
        return msg
    for piece in pieces_of_python:
        try:
            msg = msg.replace(piece, str(evaluate(bot, nick, chan, piece)))
        except BaseException:
            traceback.print_exc()
    return msg.replace('`', '')


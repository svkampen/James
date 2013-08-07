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
        message_split = msg.split('s/')[1].split('/')

        replace = message_split[0]
        by = message_split[1]

        self.message = msg
        self.to_replace = replace
        self.by = by
        self.rest = ""
        if not msg.endswith('/'):
            self.rest = message_split[2]

        self.linereq = ''

        if not msg.startswith("s/"):
            ## Probably means it has a line requirement
            self.linereq = msg.split('/')[0]

        if True:
            print("To Replace: %s" % (self.to_replace))
            print("Replace by: %s" % (self.by))
            if self.rest:
                print("Some flags: %s" % (self.rest))
            if self.linereq:
                print("Qualifiers: %s" % (self.linereq))

        if 'g' in self.rest:
            self.global_ = True
        else:
            self.global_ = False

        if 'i' in self.rest:
            self.ignorecase = True
        else:
            self.ignorecase = False


def get_message(bot, sedregex, nick, qual=None):
    if not nick in bot.state.messages:
        return ""
    for message in bot.state.messages[nick]:
        try:
            if qual:
                if re.search(sedregex, message) and re.search(qual, message):
                    return message
            else:
                if re.search(sedregex, message):
                    return message
        except BaseException:
            pass
    return ""

def check_sed(msg):
    """ Check whether a message is a sed request """
    if re.match(r"^(\S+[:,] )?(.+/)?s/.+/.*(/([gi]?){2})?$", msg):
        return True

def sed(bot, nick, chan, msg):
    """ Perform the actual sedding """
    if re.match(r"^(\S+[:,] )(.+/)?s/.+/.*(/([gi]?){2})?$", msg):
        # target acquired
        if ':' in msg.split()[0]:
            split_msg = msg.split(':')
        else:
            split_msg = msg.split(",")
        nick = split_msg[0]
        msg = split_msg[1].strip()

    sedmsg = Seddable(msg)
    if sedmsg.linereq:
        to_sed = get_message(bot, sedmsg.to_replace, nick, qual=sedmsg.linereq)
    else:
        to_sed = get_message(bot, sedmsg.to_replace, nick)

    if not to_sed:
        return

    try:
        sedmsg.message = to_sed

        if sedmsg.ignorecase and sedmsg.global_:
            # i option on
            new_msg = re.sub(sedmsg.to_replace, sedmsg.by, sedmsg.message, 
                flags=re.IGNORECASE)
        elif sedmsg.ignorecase:
            # i and g options on
            new_msg = re.sub(sedmsg.to_replace, sedmsg.by, sedmsg.message, 
                flags=re.IGNORECASE, count=1)
        elif sedmsg.global_:
            # g option on
            new_msg = re.sub(sedmsg.to_replace, sedmsg.by, sedmsg.message)
        else:
            # no options on
            new_msg = re.sub(sedmsg.to_replace, sedmsg.by, sedmsg.message, 
                count=1)


        return bot.msg(chan, "<%s> %s" % (nick, new_msg))
    except BaseException:
        traceback.print_exc()

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


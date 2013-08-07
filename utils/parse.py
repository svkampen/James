"""
IRC Parser - parse.py
"""

import inspect
import traceback
import re
import subprocess

SED_REGEX = re.compile(r"^(?:(\S+)[:,] )?(?:(.+?)/)?s/(.+?)/(.*?)(?:/([gi]{0,2}))?$")

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

def populate(sedobject, groups):
    group_types = ("target", "qual", "to_replace", "replacement", "flags")
    for k, v in zip(group_types, groups):
        setattr(sedobject, k, v)

def set_flags(sedobject, flags):
    i = 0
    count = 1
    for item in flags:
        if item == 'i':
            i += re.IGNORECASE
        if item == 'x':
            i += re.X
        if item == 'g':
            count = 0

    setattr(sedobject, 'flags', i)
    setattr(sedobject, 'count', count)

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

def sed(bot, nick, chan, msg):
    """ Perform the sedding """
    s = type('SedObject', tuple(), {})
    
    if not SED_REGEX.match(msg):
        return

    groups = SED_REGEX.match(msg).groups()
    populate(s, groups)
    set_flags(s, s.flags)

    if s.target:
        nick = s.target

    if s.qual:
        s.msg = get_message(bot, s.to_replace, nick, qual=s.qual)
    else:
        s.msg = get_message(bot, s.to_replace, nick)

    if not s.msg: return

    try:

        new_msg = re.sub(s.to_replace, s.replacement, s.msg, s.count, s.flags)

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
    if not pieces_of_python:
        return msg
    for piece in pieces_of_python:
        try:
            msg = msg.replace(piece, str(evaluate(bot, nick, chan, piece)))
        except BaseException:
            traceback.print_exc()
    return msg.replace('`', '')


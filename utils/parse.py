"""
IRC Parser - parse.py
"""

def parse(msg):
    """ blah """
    if msg.startswith("PING"):
        info = {'method': 'PING', 'arg': msg.split()[-1]}
    else:
        splitmsg = msg.split(' ', 2)
        info = {'method': splitmsg[1], 'host': splitmsg[0][1:], 'arg':
                splitmsg[2]}
    return info

def inline_python(bot, nick, chan, msg):
    """ Execute inline python """
    import inspect
    import traceback
    import re
    pieces_of_python = re.findall("`([^`]+)`", msg)
    evaluate_expression = inspect.getmodule(bot.cmdhandler.trigger('eval').function).evaluate_expression
    if pieces_of_python == []:
        return msg
    for piece in pieces_of_python:
        try:
            msg = msg.replace(piece, str(evaluate_expression(bot, nick, chan, piece)))
        except BaseException:
            traceback.print_exc()
    return msg.replace('`', '')

def check_for_sed(bot, msg):
    """ Check whether a message contains a (valid) sed statement """
    import re
    if re.match("^(\w+: )?s/.+/.+(/([gi]?){2})?$", msg):
        return True

def parse_sed(bot, sedmsg, oldmsgs):
    """ Parse a sed snippet """
    import traceback
    import re
    split_msg = sedmsg.split('/')[1:]
    glob = False
    case = False
    if len(split_msg) == 3:
        if 'g' in split_msg[2]:
            glob = True
        if 'i' in split_msg[2]:
            case = True
    try:
        regex = re.compile(split_msg[0], re.I if case else 0)
        for msg in oldmsgs:
            if regex.search(msg) is not None:
                if case:
                    return {'to_replace': "(?i)"+split_msg[0], 'replacement': lambda match: split_msg[1].replace("&", match.group(0)), 'oldmsg': msg, 'glob': glob}
                else:
                    return {'to_replace': split_msg[0], 'replacement': lambda match: split_msg[1].replace("&", match.group(0)), 'oldmsg': msg, 'glob': glob}
    except BaseException:
        traceback.print_exc()
    return -1

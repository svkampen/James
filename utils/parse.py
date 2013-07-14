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

def inline_python(bot, nick, chan, msg):
    """ Execute inline python """
    import inspect
    import traceback
    import re
    pieces_of_python = re.findall("`([^`]+)`", msg)
    if pieces_of_python == []:
        return msg
    for piece in pieces_of_python:
        try:
            msg = msg.replace(piece, str(evaluate_expression(bot, nick, chan, piece)))
        except BaseException:
            traceback.print_exc()
    return msg.replace('`', '')
""" 
Dynamically evaluate python code - James.three plugin
"""
from .util.decorators import command, require_admin, initializer
import functools

@require_admin
@command('eval', short=">>>")
def eval_it(self, nick, target, chan, arg):
    output = evaluate_expression(self, nick, chan, arg)
    if output is not None:
        self.msg(chan, output)

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

""" 
Dynamically evaluate python code - James.three plugin
"""
from .util.decorators import command, require_admin, initializer
import functools

@require_admin
@command('eval', short=">>>")
def eval_it(self, nick, target, chan, arg):
    self.msg(chan, evaluate_expression(self, nick, chan, arg))

def evaluate_expression(self, nick, chan, msg):
    """ Evaluate python code. """
    try:
        output = eval(msg)
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


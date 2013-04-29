""" 
Dynamically evaluate python code - James.three plugin
"""
from .util.decorators import command, require_admin

@require_admin
@command('eval', short=">>>")
def evaluate_expression(self, nick, chan, arg):
    """ Evaluate python code. """
    try:
        output = eval(arg)
        if output is not None:
            self.leo = output
            self._msg(chan, str(output))
    except (NameError, SyntaxError):
        try:
            exec(arg, globals())
        except NameError:
            exec(arg, globals(), locals())

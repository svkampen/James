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
            if type(self.leo) == tuple:
                self.leo = list(self.leo)
                output = list(output)
            self._msg(chan, "%s" % (output))
    except (NameError, SyntaxError):
        try:
            exec(arg, globals())
        except:
            try:
                exec(arg, locals())
            except:
                try:
                    exec(arg,globals(),locals())
                except:
                    exec(arg,locals(),globals())

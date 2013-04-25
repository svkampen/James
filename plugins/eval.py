from .util.decorators import command, require_admin

@require_admin
@command('eval', short=">>> ")
def evaluateExpression(self, nick, chan, arg):
    try:
        output = eval(arg)
        if output is not None:
            self.leo = output
            self._msg(chan, str(output))
    except:
        try:
            exec(arg, globals())
        except NameError:
            exec(arg, globals(), locals())

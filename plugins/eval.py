from util.decorators import command, require_admin

@require_admin
@command('eval', short=">>> ")
def evaluateExpression(bot, nick, chan, arg):
    try:
        output = eval(arg)
        if output is not None:
            bot.leo = output
            bot._msg(chan, str(output))
    except:
        try:
            exec(arg, globals())
        except NameError:
            exec(arg, globals(), locals())

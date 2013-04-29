from functools import wraps

def sethook(*args):
    def decorator(funct):
        bot = args[0]
        if bot.data['hooks'].get(args[1], None) == None:
            bot.data['hooks'][args[1]] = []
        hook_name = args[1]
        @wraps(funct)
        def wrapper(*args, **kwargs):
            return_value = funct(*args, **kwargs)
            for hook in bot.data['hooks'][hook_name]:
                hook(*args)
            return return_value
        return wrapper
    return decorator
            

def startinfo(*args):
    def decorator(funct):
        james_version = args[0]
        @wraps(funct)
        def wrapper(*args, **kwargs):
            print("James version %s initializing..." % (james_version))
            return funct(*args, **kwargs)
        return wrapper
    return decorator

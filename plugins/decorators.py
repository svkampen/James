#
# decorators.py - decorators
# part of James.three
# by Sam van Kampen, 2013
#

def command(*args):
    print "Hi I am a decorator"
    def decorator(funct):
        hooks = []
        for arg in args:
            hooks.append(arg)
        funct._hook = hooks
        return funct
    return decorator

""" 
 decorators.py - decorators
 part of James.three
 by Sam van Kampen, 2013
"""

def command(*args):
    """The command decorator."""
    def decorator(funct):
        """The actual command decorator."""
        print("Decorating %s" % (funct))
        hooks = []
        for arg in args:
            hooks.append(arg)
        funct.hook = hooks
        return funct
    return decorator

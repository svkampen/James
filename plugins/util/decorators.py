""" 
 decorators.py - decorators
 part of James.three
 by Sam van Kampen, 2013
"""

#def returns(outtype):
#    """A decorator that sets output type."""
#    def decorator(funct):
#        """The actual decorator"""
#        funct.output_type = outtype
#        return funct
#    return decorator
#
# Quote: "<@NightLion> Dependency injection fuck yeah"

def require_admin(funct):
    """ Decorator for requiring admin privileges. """
    funct._require_admin = True
    return funct

def initializer(funct):
    """The decorator for plugin initializer functions."""
    funct._is_plugin_initializer = True
    return funct

def command(*args, **kwargs):
    """The command decorator."""
    def decorator(funct):
        """The actual command decorator."""
        funct.hook = args
        if 'short' in kwargs.keys():
            funct.shorthook = [kwargs['short']]
        if 'category' in kwargs.keys():
            funct._category = kwargs['category']
        return funct
    return decorator

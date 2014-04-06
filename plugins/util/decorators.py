""" 
 decorators.py - decorators
 part of James.three
 by Sam van Kampen, 2013
"""

from .data import lineify as lines
from functools import wraps

class Cache(dict):
    def __init__(self, invalid=None):
        self.invalid = invalid or 128
        self.calls = 0

    def __getitem__(self, item):
        self.calls += 1
        i = super().__getitem__(item)
        if self.calls >= self.invalid:
            self.clear()
            self.calls = 0
        return i


def require_admin(funct):
    """ Decorator for requiring admin privileges. """
    funct._require_admin = True
    return funct

def initializer(funct):
    """The decorator for plugin initializer functions."""
    funct._is_plugin_initializer = True
    return funct

def cached(cache=None, get=None, action=None, insert=None, invalid=None):
    """ The cache decorator """
    if not cache:
        cache = Cache(invalid)

    if not get:
        get = lambda bot, a: str(a).lower() in cache.keys()

    if not action:
        action = lambda bot, nick, chan, a: bot.msg(chan, '\n'.join(lines(cache[a])))

    if not insert:
        insert = lambda arg, out: cache.__setitem__(arg.lower(), out)

    def decorator(funct):
        """ The actual decorator """
        @wraps(funct)
        def new_func(bot, nick, chan, arg):
            if not arg:
                return funct(bot, nick, chan, arg)

            if get(bot, arg):
                return action(bot, nick, chan, arg)

            out = funct(bot, nick, chan, arg)
            insert(arg, out)
        new_func.cache = cache
        return new_func

    return decorator

def command(*args, **kwargs):
    """The command decorator."""
    def decorator(funct):
        """The actual command decorator."""
        funct.hook = args
        if 'short' in kwargs.keys():
            funct.shorthook = [kwargs['short']]
        if 'category' in kwargs.keys():
            funct._category = kwargs['category']
        if 're' in kwargs.keys():
            funct._regex = kwargs['re']
        return funct

    return decorator



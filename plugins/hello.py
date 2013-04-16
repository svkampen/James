"""
Hello!
"""
from util.decorators import command

@command('hey', 'hello')
def hello(bot, nick, chan, arg):
    """Prints 'hello!'"""
    print("hello!")

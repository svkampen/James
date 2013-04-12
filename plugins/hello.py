"""
Hello!
"""
from decorators import command

@command('hey', 'hello')
def hello(*args):
    """Prints 'hello!'"""
    print("hello!")

from decorators import command

@command('hey', 'hello')
def randomThingy(nick, chan, arg):
    print("hello!")

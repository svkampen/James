from util.decorators import command

@command('bencode', 'binencode', 'binenc', 'benc', 'str2b')
def binencode(bot, nick, chan, arg):
    """Encode a string in binary"""
    if not arg: return bot._msg(chan, binencode.__doc__)
    return bot._msg(chan, "".join('{:08b}'.format(ord(c)) for c in arg))

@command('bdecode', 'bindecode', 'bindec', 'bdec', 'b2str')
def bindecode(bot, nick, chan, arg):
    """ Decode a number of binary zeroes """
    arg = arg.split()
    arg = ''.join(arg)
    ascii = [int(arg[i:i+8], 2) for i in xrange(0, len(arg), 8)]
    return bot._msg(chan, ''.join([chr(i) for i in ascii]))

"""
Binary codec library for James.three
"""
from .util.decorators import command


@command('bencode', 'binencode', 'binenc', 'benc', 'str2b', category='misc')
def binencode(bot, nick, target, chan, arg):
    """Encode a string in binary"""
    if not arg:
        return bot.msg(chan, binencode.__doc__)
    return bot.msg(chan, "".join('{:08b}'.format(ord(c)) for c in arg))


@command('bdecode', 'bindecode', 'bindec', 'bdec', 'b2str', category='misc')
def bindecode(bot, nick, target, chan, arg):
    """Decode a binary number."""
    arg = arg.split()
    arg = ''.join(arg)
    ascii_chrs = [int(arg[i:i+8], 2) for i in range(0, len(arg), 8)]
    return bot.msg(chan, ''.join([chr(i) for i in ascii_chrs]))

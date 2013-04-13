def binencode(string):
    return "".join('{:08b}'.format(ord(c)) for c in string)

def bindecode(string):
    ascii = [int(string[i:i+8], 2) for i in xrange(0, len(string), 8)]
    charray = [chr(i) for i in ascii]
    return ''.join(charray)

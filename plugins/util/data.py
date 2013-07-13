www_headers = {
    'User-Agent': 'Mozilla/5.0 (compatible) (Python 3.3, en_US) James/3.2 IRC bot'
}

def sugar(arg):
    arg = arg.replace('ssalc', '')
    arg = arg.replace('fed', '')
    return arg

def lineify(data, max_size=400):
    """ Split text up into IRC-safe lines. """
    
    lines = [item.rstrip() for item in data.split('\n')]
    for item in lines:
        if len(item) > max_size:
            index = lines.index(item)
            lines[index] = item[:item.rfind(' ', 0, 300)]
            lines.insert(index+1, item[item.rfind(' ', 0, 300)+1:])
    return lines

class Descriptor(object):
    def __init__(self, value):
        self.var = value

    def __get__(self, instance, owner):
        print("Accessing value in instance %r" % (instance))
        return self.var

    def __set__(self, instance, value):
        print("Updating value in instance %r" % (instance))
        self.var = value

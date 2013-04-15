class Buffer(object):
    """ 
    Represents an iterable buffer that returns completed lines.
    """
    def __init__(self):
        self.buffer = ""

    def __iter__(self):
        return self

    def next(self):
        if "\n" not in self.buffer:
            raise StopIteration
        else:
            data, self.buffer = tuple(self.buffer.split("\r\n", 1))
            return data

    def append(self, data):
        self.buffer += data
        return data

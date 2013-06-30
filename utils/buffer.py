"""
A buffer for the input stream from sockets. Iterable.
"""


class Buffer(object):
    """
    Represents an iterable buffer that returns completed lines.
    """
    def __init__(self):
        self.buffer = ""

    def __iter__(self):
        return self

    def __next__(self):
        if "\n" not in self.buffer:
            raise StopIteration
        else:
            data, self.buffer = tuple(self.buffer.split("\n", 1))
            return data.rstrip()

    def next(self):
        return self.__next__()

    def append(self, data):
        """ Append data to the buffer """
        self.buffer += data
        return data

    def get_buffer(self):
        """ Make pylint shut up """
        print(self.buffer)

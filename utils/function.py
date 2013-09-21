"""
Function object
"""

class Function(object):
    """ Function(fn function, tuple args=None) """
    def __init__(self, function, args=None):
        self.func = function
        self.args = args

    def call(self):
        if self.args:
            self.func(*self.args)
        else:
            self.func()

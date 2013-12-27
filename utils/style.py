"""
Style module
"""

class Styler(object):
    """ A styler """

    def bold(string):
        return "\x02%s\x02" % (string)

    def underline(string):
        return "\x1F%s\x1F" % (string)


    def overline(text):
        return ''.join(["\u0305" + x for x in text])

    def strikethrough(text):
        return ''.join(["\u0336" + x for x in text])
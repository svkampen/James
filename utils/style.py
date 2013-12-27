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
        return "\u0305".join(text) + "\u0305"

    def strikethrough(text):
        return "\u0336".join(text) + "\u0336"
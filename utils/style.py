"""
Style module
"""

colors = {
    'white'  : '00',
    'black'  : '01',
    'blue'   : '02',
    'green'  : '03',
    'red'    : '04',
    'brown'  : '05',
    'purple' : '06',
    'orange' : '07',
    'yellow' : '08',
    'lime'   : '09',
    'teal'   : '10',
    'cyan'   : '11',
    'lblue'  : '12',
    'pink'   : '13',
    'grey'   : '14',
    'silver' : '15'
}

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

    def color(text, color="red", background=None):
        if background:
            return "\x03%s,%s%s\x03%s,%s" % (colors[color], colors[background],
             text, colors[color], colors[background])
        return "\x03%s%s\x03%s" % (colors[color], text, colors[color])
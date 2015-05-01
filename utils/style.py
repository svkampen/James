"""
Style module
"""

import re
import inspect
import random
from plugins import rainbow

COLOR_EXTRACT = re.compile("(^|.*?)(\x03...+?)\x0f([^\x03]+|$)")

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
    'gray'   : '14',
    'silver' : '15'
}

class Styler(object):
    """ A styler """

    def sopa(self, string):
        return (re.sub(r"\S+", lambda m: "\x16%s\x0F" % (" "*len(m.group(0))),
            string) + " #fightsopa")

    def bold(self, string):
        return "\x02%s\x02" % (string)

    def underline(self, string):
        return "\x1F%s\x1F" % (string)

    def rainbow(self, string):
        return rainbow.rainbow(re.sub("\x03\d{2}", "", string, count=0))


    def overline(self, text):
        return ''.join(["\u0305" + x for x in text])

    def strikethrough(self, text):
        return ''.join(["\u0336" + x for x in text])

    def color(self, text, color="red", background=None):
        if background:
            return "\x03%s,%s%s\x0f" % (colors[color], colors[background], text)
        return "\x03%s%s\x0f" % (colors[color], text)

    def merge_colors(self, color, message):
        if not ('\x03' in message):
            return color(message)
        
        output = []
        
        parts = COLOR_EXTRACT.findall(message)        

        for (before, colored, after) in parts:
            if (before):
                output.append(color(before))
            output.append(colored)
            if (after):
                output.append(color(after))
        
        output = self.minify(''.join(output))
        return output

    def control_reduce(self, data):
        """ Reduce a set of control codes to simplest form. """
        data = data.group(0)

        # Step 1: Delete all control codes before a reset.
        reset = ""
        if "\x0f" in data:
            data = data.rsplit("\x0f", 1)[-1]
            reset = "\x0f"

        # Step 2. Pull out the control codes. \x03s go first, then the rest.
        colors = re.findall(r"\x03\d?\d?(?:,\d\d?)?", data)
        data = re.sub(r"(\x03\d?\d?(?:,\d\d?)?)", "", data)
        data = "".join(sorted(data))

        # Step 3a. Delete cancelling control codes.
        data = re.sub(r"([\x1d\x02\x1f\x16])\1", "", data)

        # Step 3b. Merge colour codes.
        if colors:
            colors = [i[1:] for i in colors]
            fg, bg = None, None
            for i in colors:
                if i == "":
                    fg, bg = None, None
                elif "," not in i:
                    fg = i
                elif i.startswith(","):
                    bg = i[1:]
                else:
                    fg, bg = i.split(",")
            if fg == bg == None:
                color = "\x03"
            elif fg == None:
                color = "\x03," + bg
            elif bg == None:
                color = "\x03" + fg
            else:
                color = "\x03%s,%s" % (fg, bg)

            data = color + data

        return reset + data

    def minify(self, data):
        """ Rearrange and rewrite control codes to shorten the message. """
        if "\n" in data:
            return "\n".join(map(minify, data.split("\n")))

        # Step 1. Reduce all contiguous blocks of control codes.
        data = re.sub(r"([\x1d\x02\x1f\x0f\x16]|\x03\d?\d?(,\d\d?)?)+", self.control_reduce, data)

        # Step 2. Get rid of redundant colour codes.
        colors = None, None
        toggles = dict(zip("\x1d\x02\x1f\x16", (False, False, False, False)))
        reduced = []
        for i in re.split(r"([\x1d\x02\x1f\x0f\x16]|\x03\d?\d?(?:,\d\d?)?)", data):
            if not re.match(r"([\x1d\x02\x1f\x0f\x16]|\x03\d?\d?(?:,\d\d?)?)", i):
                reduced.append(i)
            elif i in toggles:
                # Redundant toggles are already cancelled.
                toggles[i] = not toggles[i]
                reduced.append(i)
            elif i == "\x0f" and not any(toggles.values()) and not any(colors):
                reduced.append(i)
            elif i.startswith("\x03"):
                codes = i[1:].split(",")
                if codes == ("",) and any(colors):
                    reduced.append(i)
                elif len(codes) == 1 and colors[0] != codes[0]:
                    reduced.append(i)
                elif len(codes) == 2:
                    codes = [i if i else None for i in codes]
                    codes = ["" if x == y else x for x, y in zip(codes, colors)]
                    reduced.append("\x03" + ",".join(codes).rstrip(","))
        data = "".join(reduced)

        # Step 2.5. Get rid of codes which cancel each other out
        data = re.sub(r"\x0f(\x03..)", r"\1", data)

        # Step 3. Shorten colour codes.
        # If it has a background and is 2 digits starting with 0
        # the 0 is omitted.
        data = re.sub(r"\x030(\d),", r"\x03\1,", data)
        
        # If the character following is not a digit, and the adjacent code starts with 0
        # the 0 is omitted.
        data = re.sub(r"(\x03(?:\d?\d?,)?)0(\d[^\d])", r"\1\2", data)

        # Step 4. Get rid of trailing codes.
        data = re.sub(r"([\x1d\x02\x1f\x0f\x16]|\x03\d?\d?(,\d\d?)?)+$", "", data)

        return data

    def random(self, msg):
        words = msg.split()
        done_words = []
        rand = lambda: random.randint(0,14)
        for word in words:
            done_words.append("\x03%.2d%s" % (rand(), word))

        msg = ' '.join(done_words)
        return msg

    def random_slow(self, msg):
        return self.minify(self.random(msg))

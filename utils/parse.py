""" 
IRC Parser - parse.py
"""

import sys

def parse(msg):
    """ Parse placeholder """
    return msg

class Parse(object):
    """ Parser """
    def __call__(self, msg):
        return self.parse(msg)

    def parse(self, msg):
        """ Parse a string """
        if msg.startswith("PING"):
            info = {'method': 'PING', 'arg': msg.split()[-1]}
        else:
            splitmsg = msg.split(' ', 2)
            info = {'method': splitmsg[1], 'host': splitmsg[0][1:], 'arg':\
                    splitmsg[2]}
        return info

    def check_for_sed(self, bot, nick, msg):
        import re
        if re.match("^(\w+: )?s/.+/.+(/([gi]?){2})?$", msg):
            return True

    def parse_sed(self, bot, sedmsg, oldmsgs):
        import re
        split_msg = sedmsg.split('/')[1:]
        glob = False
        flags = 0
        if len(split_msg) == 3:
            if 'g' in split_msg[2]:
                glob = True
            if 'i' in split_msg[2]:
                flags = flags or re.I
        regex = re.compile(split_msg[0])
        for msg in oldmsgs:
            if regex.search(msg) is not None:
                return {'to_replace': split_msg[0], 'replacement': split_msg[1], 'oldmsg': msg, 'glob': glob, 'flags': flags}
        return -1

    def copy(self):
        """ Copy this Parse instance """
        return self

sys.modules[__name__]  = Parse()

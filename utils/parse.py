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
        #match = re.match("^(\w+: )?s/.+/.+(/[g]?)?$", msg)
        if msg.startswith('s/') and msg.count('/') > 2:
            return True

    def parse_sed(self, bot, sedmsg, oldmsgs):
        import re
        split_msg = sedmsg.split('/')[1:]
        regex = re.compile(split_msg[0])
        for msg in reversed(oldmsgs):
            if regex.search(msg) is not None:
                return {'to_replace': split_msg[0], 'replacement': split_msg[1], 'oldmsg': msg, 'args': split_msg[2]}
        return -1

    def copy(self):
        """ Copy this Parse instance """
        return self

sys.modules[__name__]  = Parse()

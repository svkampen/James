"""
Message object "n stuff
"""

from .channel import Channel
from datetime import datetime
import re

ACTION_RE = re.compile(r'\x01ACTION (.+)\x01')

class Message(object):
    def __init__(self, user, chan, msg, timestamp=None):
        self.nick = user
        self.channel = chan
        self.msg = msg
        self.is_action = False

        match = ACTION_RE.match(msg)

        if (match):
            self.msg = match.group(1)
            self.is_action = True

        self.timestamp = timestamp or datetime.utcnow()


    def __call__(self, *args):
        return self.msg

    def __repr__(self):
        return "Message(user=%r, chan=%r, msg=%r, timestamp=%r)" % (self.nick, self.channel,
                                                                    self.msg, self.timestamp)

    def __str__(self):
        timestamp = "[%s ago]"
        timestamp = timestamp % (str(datetime.utcnow() - self.timestamp).rsplit(':', 1)[0])
        return "%s <%s> %s" % (timestamp, self.nick, self.msg)

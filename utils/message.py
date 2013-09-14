"""
Message object 'n stuff
"""

from .channel import Channel
from datetime import datetime

class Message(object):
	def __init__(self, user, chan, msg, timestamp=None):
		self.nick = user
		self.channel = chan
		self.msg = msg
		self.timestamp = timestamp or datetime.now().isoformat()

	def __call__(self, *args):
		return self.msg

	def __repr__(self):
		return "Message(user=%r, chan=%r, msg=%r)" % (self.nick, self.channel, self.msg)
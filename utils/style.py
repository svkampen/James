"""
Style module
"""

class Styler(object):
	""" A styler """
	@staticmethod
	def bold(string):
		return "\x02%s\x02" % (string)
	@staticmethod
	def underline(string):
		return "\x1F%s\x1F" % (string)
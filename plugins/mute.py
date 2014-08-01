"""
Mute/Unmute users
"""
from .util.decorators import command, require_admin
from .util.data import get_doc

@require_admin
@command("mute", category="meta")
def mute(self, nick, chan, arg):
    """ mute <nick> -> Prohibit someone from using the bot. Admin-only. """
    if not arg:
    	return bot.msg(chan, get_doc())
    self.state.mute(arg)
    self.msg(chan, "%s: You are temporarily prohibited from using this bot" % (arg))


@require_admin
@command("unmute", category="meta")
def unmute(self, nick, chan, arg):
    """ unmute <nick> -> Let someone use the bot. Admin-only. """
    if not arg:
    	bot.msg(chan, get_doc())
    self.state.unmute(arg)
    self.msg(chan, "%s: You are now allowed to use this bot" % (arg))

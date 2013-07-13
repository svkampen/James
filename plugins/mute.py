"""
Mute/Unmute users
"""
from .util.decorators import command, require_admin


@require_admin
@command('mute', category='meta')
def mute(self, nick, target, chan, arg):
    self.state.mute(arg)
    self.msg(chan, "%s: You are temporarily prohibited from using this bot" % (arg))


@require_admin
@command('unmute', category='meta')
def unmute(self, nick, target, chan, arg):
    self.state.unmute(arg)
    self.msg(chan, "%s: You are now allowed to use this bot" % (arg))

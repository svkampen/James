""" 
Mute/Unmute users
"""
from .util.decorators import command, require_admin, initializer

@require_admin
@command('mute')
def mute(self, nick, target, chan, arg):
    self.state.mute(arg)
    self.msg(chan, "%s: You are temporarily prohibited from using this bot"%(arg))

@require_admin
@command('unmute')
def unmute(self, nick, target, chan, arg):
    self.state.unmute(arg)
    self.msg(chan, "%s: You are now allowed to use this bot"%(arg))

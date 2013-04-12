from decorators import command, returns
import os

@returns('msg_out')
@command('bash', short='$')
def bash(nick, chan, arg):
    """Execute a bash command"""
    return os.popen(arg).read()

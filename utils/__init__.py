""" Initializer for the package utils. """
from . import command
from . import commandhandler
from . import parse
from . import num
from . import events
from . import message
from . import channel
from types import ModuleType, FunctionType
import inspect

def get_name(f):
    if type(f) == ModuleType:
        return f.__name__
    elif type(f) == FunctionType:
        return "%s.%s" % (inspect.getmodule(f).__name__, f.__name__)
    else:
        try:
            return f.__name__
        except AttributeError:
            return "unknown"

def is_enabled(bot, chan, command):
    c = bot.state.channels.get(chan, False)
    if get_name(command.function) in c.disabled_commands:
        return False
    elif get_name(command.function).rsplit('.', 1)[0] in c.disabled_commands:
        return False
    return True
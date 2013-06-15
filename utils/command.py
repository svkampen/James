""" 
 command class definition - do not confuse this with
 the individual plugins in plugins/
 by Sam van Kampen, 2013 
"""

import sys
import traceback

class Command(object):
    """Command(Object function, List<str> hooks=[], List<str> shorthooks=[])"""
    def __init__(self, function, hooks=None, shorthooks=None):
        self.function = function
        if not hooks:
            hooks = []
        if not shorthooks:
            shorthooks = []
        self.hooks = hooks
        self.short_hooks = shorthooks
        self.main_hook = self.hooks[0]

    def __call__(self, *args):
        """ Call the function embedded in the command """
        return self.function(*args)

    def get_function(self):
        """Get the function associated with this command"""
        return self.function

    def set_hooks(self, hooks):
        """ Set the hooks. """
        self.hooks = hooks

    def set_shorthooks(self, hooks):
        """ Set the shorthook(s) """
        self.short_hooks = hooks

    def is_triggered_by(self, trigger, short=False):
        """Check whether this command is triggered by <trigger>"""
        if short:
            return True if trigger in self.short_hooks else False
        else:
            return True if trigger in self.hooks else False

def plugins_to_commands(plugins):
    """Turn a list of plugins into a list of commands"""
    commands = []
    has_hook=False
    if type(plugins) == type(sys.modules[__name__]):
        plugins = [plugins]
    try:
        for plugin in plugins:
            for function in plugin.__dict__.values():
                if hasattr(function, "hook"):
                    has_hook = True
                    new_command = Command(function, function.hook)
                if hasattr(function, "shorthook") and has_hook == True:
                    new_command.set_shorthooks(function.shorthook)
                if has_hook:
                    commands.append(new_command)
                    has_hook = False
    except BaseException:
        traceback.print_exc()

    return commands

def plugins_to_initializers(plugins):
    """Turn a list of plugins into a list of initializers"""
    initializers = []
    if type(plugins) == type(sys.modules[__name__]):
        plugins = [plugins]
    try:
        for plugin in plugins:
            for function in plugin.__dict__.values():
                if hasattr(function, "_is_plugin_initializer"):
                    initializers.append(function)
    except BaseException:
        traceback.print_exc()
    return initializers

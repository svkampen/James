""" 
 command class definition - do not confuse this with
 the individual plugins in plugins/
 by Sam van Kampen, 2013 
"""

import sys

class Command():
    """ Command(Object function, List<string> hooks) - A command."""
    def __init__(self, function, hooks):
        self.function = function
        self.hooks = hooks

    def __call__(self):
        return self.function()

    def get_function(self):
        """Get the function associated with this command"""
        return self.function

    def is_triggered_by(self, trigger):
        """Check whether this command is triggered by <trigger>"""
        return True if trigger in self.hooks else False

def plugins_to_commands(plugins):
    """Turn a list of plugins into a list of commands"""
    commands = []
    if type(plugins) == type(sys.modules[__name__]):
        plugins = [plugins]
    for plugin in plugins:
        for function in plugin.__dict__.itervalues():
            if hasattr(function, "hook"):
                commands.append(Command(function, function.hook))
    return commands

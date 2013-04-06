#
# command class definition - do not confuse this with the individual commands in plugins/
# by Sam van Kampen, 2013
#

import sys

class Command():
    """ Command(Object function, List<string> hooks) - A command."""
    def __init__(self, function, hooks):
        self.function = function
        self.hooks = hooks

    def getFunction(self):
        return self.function

    def isTriggeredBy(self, trigger):
        return True if trigger in self.hooks else False

def pluginsToCommands(plugins):
    if type(plugins) == type(sys.modules[__name__]):
        plugins = [plugins]
    for plugin in plugins:
        for function in plugin.__dict__.itervalues():
            if hasattr(function, "_hook"):
                commands.append(Command(function, function._hook))

    return commands


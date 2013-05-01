""" 
The Command handler
"""
from . import command
try:
    import command
except:
    pass

class CommandHandler():
    """ The command handler object - handles triggering commands """
    def __init__(self, bot, plugins):
        self.initializers = command.plugins_to_initializers(plugins)
        for function in self.initializers:
            function(bot)
        self.commands = command.plugins_to_commands(plugins)
        self.command_names = [command.main_hook for command in self.commands]
        if self.commands == []:
            raise RuntimeError("No commands found!")
        print("%d commands initialized." % (len(self.commands)))

    def trigger(self, trigger):
        """ Try to trigger a command with hook <trigger> """
        for command_ in self.commands:
            if command_.is_triggered_by(trigger):
                return command_
               
        return False

    def trigger_short(self, trigger):
        """ Try to trigger a command with shorthook <trigger> """
        for command_ in self.commands:
            if command_.is_triggered_by(trigger, short=True):
                return command_

        return False

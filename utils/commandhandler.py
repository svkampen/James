""" 
The Command handler
"""
from . import command

class CommandHandler():
    """ The command handler object - handles triggering commands """
    def __init__(self, bot, plugins):
        self.initializers = command.plugins_to_initializers(plugins)
        for function in self.initializers:
            function(bot)
        self.commands = command.plugins_to_commands(plugins)
        if self.commands == []:
            raise RuntimeError("No commands found!")

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

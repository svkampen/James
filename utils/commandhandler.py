""" 
The Command handler
"""
from . import command

class CommandHandler():
    def __init__(self, bot, plugins):
        self.initializers = command.plugins_to_initializers(plugins)
        for function in self.initializers:
            function(bot)
        self.commands = command.plugins_to_commands(plugins)
        if self.commands == []:
            raise RuntimeError("No commands found!")

    def trigger(self, trigger):
        hasFoundCommand = False
        for command in self.commands:
            if command.is_triggered_by(trigger):
                hasFoundCommand = True
                return command
               
        return False

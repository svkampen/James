""" 
The Command handler
"""
import command
from straight.plugin import load

class CommandHandler():
    def __init__(self, plugins):
        self.commands = command.plugins_to_commands(load(plugins)._plugins)
        if self.commands == []:
            raise RuntimeError("No commands found!")

    def trigger(self, trigger):
        hasFoundCommand = False
        for command in self.commands:
            if command.is_triggered_by(trigger):
                hasFoundCommand = True
                return command
               
        return False

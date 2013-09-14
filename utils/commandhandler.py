"""
The Command handler
"""
from . import command


class CommandHandler():
    """ The command handler object - handles triggering commands """
    def __init__(self, bot, plugins):

        self.initializers = self.commands = []

        self.initializers = command.plugins_to_initializers(plugins)
        for function in self.initializers:
            function(bot)
        self.commands = command.plugins_to_commands(plugins)
        self.command_names = [cmd.main_hook for cmd in self.commands]

        self.command_help = self.organize_commands(self.commands)

        if self.commands == []:
            raise RuntimeError("No commands found!")
        print("%d commands initialized." % (len(self.commands)))

    def organize_commands(self, commands):
        categories = set()
        command_help = {}
        categories.add("unknown")
        for command in commands:
            if hasattr(command.function, '_category'):
                categories.add(command.function._category)
        for category in categories:
            command_help.update({category: set()})
        for command in commands:
            if hasattr(command.function, '_category'):
                command_help[command.function._category].add(command.main_hook)
            else:
                command_help['unknown'].add(command.main_hook)
        del categories
        return command_help


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

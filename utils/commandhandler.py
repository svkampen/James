#
#
#
import command

class CommandHandler():
    def __init__(self, plugins):
        self.commands = command.plugins_to_commands(plugins)

    def trigger(self, trigger):
        hasFoundCommand = False
        for command in self.commands:
            if command.is_triggered_by(trigger):
                hasFoundCommand = True
                
        return hasFoundCommand

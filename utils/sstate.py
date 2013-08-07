"""
ServerState object
"""


class ServerState(object):
    """ A class that holds the active channels and admins and some more things about the bot that are server-specific. """
    def __init__(self):
        self.admins = set()
        self.muted = set()
        self.nick = 'JamesNext'
        self.notices = []
        self.messages = {}

    def add_admin(self, nick):
        """ Add an user to the admin list. """
        self.admins.add(nick.lower())

    def del_admin(self, dnick):
        """ Remove an user from the admin list. """
        self.admins.remove(dnick.lower())

    def mute(self, nick):
        """ Add an user to the mute list. """
        self.muted.add(nick.lower())

    def unmute(self, dnick):
        """ Remove an user from the block list. """
        self.muted.remove(dnick.lower())

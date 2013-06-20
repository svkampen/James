""" 
Channel and ServerState objects
"""

class ServerState(object):
    """ A class that holds the active channels and admins and some more things about the bot that are server-specific. """
    def __init__(self):
        self.admins = [] # moved this to the config ('admins') ._. wondered why it duplicated you
        self.nick = 'JamesNext'
        self.notices = []
    
    def add_admin(self, nick):
        """ Add an admin to the admin list. """
        self.admins.append(nick.lower())

    def del_admin(self, dnick):
        """ Remove an admin from the admin list. """
        dnick = dnick.lower()
        self.admins = [nick for nick in self.admins if nick != dnick]

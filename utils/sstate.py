""" 
Channel and ServerState objects
"""

class Channel(object):
    """ An IRC channel. """
    def __init__(self, name, users, topic=None):
        self.identifier = name.lower()
        self.name = name.lower()
        self.users = users
        self.topic = topic

    def __repr__(self):
        return "Channel(name=%r, users=%r, topic=%r)" % (self.name, self.users, self.topic)

    def set_topic(self, topic):
        """ Set the channel topic. """
        self.topic = topic

    def set_users(self, users):
        """ Set the users in the channel. """
        self.users = users

    def set_user(self, olduser, user):
        """ Set olduser to user """
        temp_users = []
        for currentuser in self.users:
            if currentuser == olduser:
                temp_users.append(user)
            else:
                temp_users.append(currentuser)
        self.users = temp_users
        return self.users
        

    def add_user(self, user):
        """ Add a user to the users list. """
        if not user.lower() in self.users:
            self.users.append(user.lower())

    def remove_user(self, ruser):
        """ Remove a user from the user list. """
        ruser = ruser.lower()
        [self.users.remove(ruser) for user in self.users if user == ruser]
    

class ServerState(object):
    """ A class that holds the active channels and admins and some more things about the bot that are server-specific. """
    def __init__(self):
        self.channels = []
        self.admins = ['svkampen', 'lion', 'kvasir']
        self.nick = 'JamesNext'
        self.notices = []
    
    def add_admin(self, nick):
        """ Add an admin to the admin list. """
        self.admins.append(nick.lower())

    def get_channels(self):
        """ Get all channels, in string form. """
        return [chan.name.lower() for chan in self.channels]

    def get_channel(self, channel):
        """ Get a channel. """
        return [chan for chan in self.channels if chan.name == channel]

    def get_channels_for_user(self, user):
        """ Get every chan that contains user """
        return [chan for chan in self.channels if user in chan.users]

    def del_admin(self, dnick):
        """ Remove an admin from the admin list. """
        dnick = dnick.lower()
        self.admins = [nick for nick in self.admins if nick != dnick]
    
    def add_channel(self, identifier, users, topic=None):
        """ Add a channel to the channel list. """
        self.channels.append(Channel(identifier, users, topic=topic))
        return self.channels[-1]

    def rm_channel(self, identifier):
        """ Remove a channel from the channel list. """
        self.channels = [c for c in self.channels if c.name != identifier]

    def del_channel(self, identifier):
        """ Remove a channel from the channel list. """
        self.rm_channel(identifier)

    def set_channel_users(self, chan_, users):
        """ Set the users for a channel. """
        for chan in self.channels:
            if chan.name.lower() == chan_.lower():
                chan.set_users(users)

    def set_channel_topic(self, chan_, topic):
        """ Set topic for a channel. """
        for chan in self.channels:
            if chan.name == chan_:
                chan.set_topic(topic)

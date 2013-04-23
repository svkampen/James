""" 
Blah things
"""

class Channel(object):
    def __init__(self, name, users, topic=None):
        self.identifier = name
        self.name = name
        self.users = users
        self.topic = topic

    def set_topic(self, topic):
        self.topic = topic

    def set_users(self, users):
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
        if not user in self.users:
            self.users.append(user)

    def remove_user(self, ruser):
        [self.users.remove(ruser) for user in self.users if user == ruser]
    

class ServerState(object):
    def __init__(self):
        self.channels = []
        self.admins = ['svkampen', 'Lion']
    
    def add_admin(self, nick):
        self.admins.append(nick)

    def get_channels(self):
        return [chan.name for chan in self.channels]

    def get_channel(self, channel):
        return [chan for chan in self.channels if chan.name == channel]

    def get_channels_for_user(self, user):
        return [chan for chan in self.channels if user in chan.users]

    def del_admin(self, dnick):
        [self.admins.remove(nick) for nick in self.admins if nick == dnick]
    
    def add_channel(self, identifier, users, topic=None):
        self.channels.append(Channel(identifier, users, topic=topic))
        return self.channels[-1]

    def rm_channel(self, identifier):
        [self.channels.remove(c) for c in self.channels if c.name == identifier]

    def del_channel(self, identifier):
        self.rm_channel(identifier)

    def set_channel_users(self, channel, users):
        [chan.set_users(users) for chan in self.channels if chan.name == channel]

    def set_channel_topic(self, channel, topic):
        [chan.set_topic(topic) for chan in self.channels if chan.name == channel]

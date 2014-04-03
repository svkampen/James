""" 
Do channel STUFF
"""

import sys
from subprocess import Popen
import time
from datetime import datetime

bot = None

class MagicAttribute(object):
    """ A magic attribute """
    def __get__(self, obj, type):
        return getattr(self, "func")(obj)

class IsUserSetEmpty(MagicAttribute):
    def func(self, obj):
        return True if not obj.users else False

class UserNumInChannel(MagicAttribute):
    def func(self, obj):
        return len(obj.users) if not obj.is_empty else -1

class IsIdentified(MagicAttribute):
    def func(self, obj):
        bot.msg("NickServ", "ACC %s" % (obj.nick))
        time.sleep(4/3)
        return "3" in bot.state.notices[-1]["message"]

class ChannelModes(MagicAttribute):
    def func(self, obj):
        bot._send("MODE %s" % (obj.name))
        time.sleep(4/3)
        return obj.modes_

class UserMessagesArray(MagicAttribute):
    def func(self, obj):
        return bot.state.messages[obj.nick]

class UserChannels(MagicAttribute):
    def __init__(self):
        self.state = bot.state
    def func(self, obj):
        return self.state.channels.get_channels_for(obj.nick)

class UserIdleTime(MagicAttribute):
    def func(self, obj):
        current_time = datetime.utcnow()
        last_m_time = obj.messages[0].timestamp
        difference = (current_time - last_m_time)
        return difference


class User(object):
    def __init__(self, nick, channels=None):
        self.nick = nick
        
        self.is_identified = IsIdentified()
        self.messages = UserMessagesArray()
        self.idle_time = UserIdleTime()
        self.channels = UserChannels()
        self.exactnick = ""

    def __repr__(self):
        return "User(nick=%r, channels=%s)" % (self.nick, self.channels.keys())

    def kick(self, channel):
        bot._send("KICK %s %s :Requested" % (channel, self.nick))

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if hasattr(attr, "__get__"):
            return attr.__get__(self, User)
        return attr

class UserDict(dict):
    """ A dictionary with users """
    def __init__(self, bot_server=None):
        if bot_server:
            global bot
            bot = bot_server

    def get(self, *args, **kwargs):
        args = list(args)
        try:
            args[0] = args[0].lower()
        except AttributeError:
            raise TypeError("Argument 0 should be of type str, not %s" % (type(args[0])))
        return super().get(*args, **kwargs)

    def __str__(self):
        return "UserDict"

    def discard(self, item):
        try:
            del self[item]
        except KeyError:
            pass

    def __setitem__(self, item, value):
        super().__setitem__(item, value)

    def __getattribute__(self, item):
        if item != "keys":
            if item in self.keys():
                return self[item]
        if item in dir(UserDict):
            return super().__getattribute__(item)
        else:
            raise AttributeError("'%s' object has no attribute '%s', is '%s' in the channel?"
                % (self, item, item))

class Channel(object):
    # TODO: ADD KICK STUFF
    def __init__(self, name):
        self.name = name
        self.disabled_commands = set()
        self.users = UserDict()
        self.is_empty = IsUserSetEmpty()
        self.users_n = UserNumInChannel()
        self.state = bot.state

    def add_user(self, user):
        assert user == user.lower(), "User is passed as lowercase."
        existing_user = self.state.users.get(user, False)
        if existing_user:
            self.users[user] = existing_user
        else:
            self.state.users[user] = User(user)
            self.users[user] = self.state.users[user]

    def remove_user(self, user):
        del self.users[user.lower()]

    def change_user(self, map_):
        uobj = self.users[map_[0]]
        uobj.nick = map_[1]
        self.users.discard(map_[0])
        self.users[map_[1]] = uobj
        return self.users[map_[1]]

    def update_users(self, update):
        update = [u.lower() for u in update]
        for user in update:
            existing_user = self.state.users.get(user, False)
            if existing_user:
                self.users[user] = existing_user
            else:
                self.state.users[user] = User(user)
                self.users[user] = self.state.users.get(user)
        return self.users

    def __repr__(self):
        return "Channel(name=%r)" % (self.name)

    def __call__(self):
        return self.name

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if hasattr(attr, "__get__"):
            return attr.__get__(self, Channel)
        return attr

class UnknownChannel(Channel):
    def __init__(self, name):
        self.name = name
        self.known = False

    def __dir__(self):
        if self.known:
            return Channel.__dir__(Channel(""))
        else:
            return [i for i in dir(Channel) if i.startswith("_")] + ["name", "known", "join"]

    def join(self):
        if not self.known:
            bot._send("JOIN %s" % (self.name))
            self.known = True

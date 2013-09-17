""" 
Do channel STUFF
"""

import sys
from subprocess import Popen
import time
from datetime import datetime

class MagicAttribute(object):
    """ A magic attribute """
    def __get__(self, obj, type):
        return getattr(self, 'func')(obj)

class IsUserSetEmpty(MagicAttribute):
    def func(self, obj):
        return True if not obj.users else False

class UserNumInChannel(MagicAttribute):
    def func(self, obj):
        return len(obj.users) if not obj.is_empty else -1

class IsIdentified(MagicAttribute):
    def __init__(self):
        self.bot = sys.modules['__main__'].BOT
    def func(self, obj):
        self.bot.msg("NickServ", "ACC %s" % (obj.nick))
        time.sleep(4/3)
        return '3' in self.bot.state.notices[-1]['message']

class ChannelModes(MagicAttribute):
    def __init__(self):
        self.bot = sys.modules['__main__'].BOT
    def func(self, obj):
        self.bot._send("MODE %s" % (obj.name))
        time.sleep(4/3)
        return obj._modes

class UserMessagesArray(MagicAttribute):
    def __init__(self):
        self.bot = sys.modules['__main__'].BOT
    def func(self, obj):
        return bot.state.messages[obj.nick]

class UserIdleTime(MagicAttribute):
    def func(self, obj):
        current_time = datetime.utcnow()
        last_m_time = obj.messages[-1].timestamp
        difference = (current_time - last_m_time)

class User(object):
    def __init__(self, nick):
        self.nick = nick
        self.is_identified = IsIdentified()
        self.messages = UserMessagesArray()
        self.idle_time = UserIdleTime()

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if hasattr(attr, "__get__"):
            return attr.__get__(self, Channel)
        return attr

class UserDict(dict):
    """ A dictionary with users """
    def get(self, *args, **kwargs):
        try:
            args[0] = args[0].lower()
        except AttributeError:
            raise TypeError("Argument 0 should be of type str, not %s" % (type(args[0])))
        return super().get(*args, **kwargs)

    def __str__(self):
        return 'UserDict'

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
        self.users = {}
        self.is_empty = IsUserSetEmpty()
        self.users_n = UserNumInChannel()
        self.modes = ChannelModes()

    def add_user(self, user):
        print('adding user %s to channel %s' % (user, self.name))
        self.users[user] = User(user.lower())

    def remove_user(self, user):
        try:
            del self.users[user]
        except KeyError:
            pass

    def change_user(self, map_):
        self.remove_user(map_[0])
        self.add_user(map_[1])

    def update_users(self, update):
        print("updating channel %s with users: %s" % (self.name, update))
        for user in update:
            self.users[user] = User(user.lower())
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
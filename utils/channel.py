""" 
Do channel STUFF
"""

import sys
from subprocess import Popen

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

class Channel(object):
    # TODO: ADD KICK STUFF
    def __init__(self, name):
        self.name = name
        self.users = set()
        self.is_empty = IsUserSetEmpty()
        self.users_n = UserNumInChannel()

    def add_user(self, user):
        self.users.add(user.lower())

    def remove_user(self, user):
        self.users.remove(user.lower())

    def change_user(self, map_):
        self.users.discard(map_[0])
        self.users.add(map_[1])

    def update_users(self, update):
        self.users |= set([i.lower() for i in list(update)])
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
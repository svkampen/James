"""
Miscellaneous stuff.
"""

from .util.decorators import command
import datetime
import random


@command('misc.day_at', category='misc')
def get_weekday_at(bot, nick, target, chan, arg):
    """
    Get the day of the week at <date>
    <date> format: yyyy-mm-dd
    """
    if not arg:
        return get_weekday_at.__doc__.lstrip()
    arg = arg.split('-')
    year, month, day = (int(item) for item in (arg[0], arg[1], arg[2]))
    time = datetime.datetime(year, month, day)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday = days[time.weekday()]
    bot.msg(chan, "The day of the week on \x02%s\x02 was %s" % ('-'.join(arg), weekday))


@command('unibarf', short='barf', category='"language"')
def unicode_please(bot, nick, target, chan, arg):
    """ Return a random number of unicode characters, or <arg> amount of unicode characters. """
    if not arg:
        arg = random.randint(2, 400)
    arg = int(arg)
    startpos = random.randint(1000, 0xFFFF)
    endpos = startpos + arg
    bot.msg(chan, "%s" % (''.join([chr(i) for i in range(startpos, endpos)])))

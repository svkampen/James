"""
Age Calculator
"""

from .util.decorators import command, cached
from .util.data import get_doc
import datetime

@command("ageme", category="misc")
def ageme(bot, nick, chan, arg):
    """ ageme day month year -> Find exact age of person """
    if not arg:
        return bot.msg(chan, get_doc())

    prec = "16"
    args = arg.split()
    if len(args) == 3:
        (day, month, year) = args
    elif len(args) == 4:
        (day, month, year, prec) = args
    elif len(args) == 5:
        (day, month, year, prec, chan) = args
    else:
        return bot.msg(chan, ageme.__doc__.strip())

    try:
        int(month)
    except ValueError:
        if len(month) > 2 and month[:3].lower() in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]:
            month = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"].index(month[:3].lower())+1
    try:
        int(prec)
        if int(prec) > 200 or int(prec) < 0:
            raise ValueError
    except ValueError:
        return bot.msg(chan, ageme.__doc__.strip())

    try:
        age = ("%." + prec + "f") % ((datetime.datetime.now() - datetime.datetime(int(year), int(month), int(day))).total_seconds() / (60 * 60 * 24 * 365.242))
    except BaseException as e:
        return bot.msg(chan, str(e)+": Error parsing date. Are you american?")

    output = "%s: you are %s years old." % (nick, age)

    bot._msg(chan, output)

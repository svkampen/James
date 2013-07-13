"""
Age Calculator
"""

from .util.decorators import command
import datetime
import time


@command('ageme', category='misc')
def insult(bot, nick, target, chan, arg):
    """ Find exact age of person """
    if not arg:
        return bot.msg(chan, insult.__doc__.strip())

    prec = '16'
    args = arg.split()
    if len(args) == 3:
        (day, month, year) = args
    elif len(args) == 4:
        (day, month, year, prec) = args
    elif len(args) == 5:
        (day, month, year, prec, chan) = args
    else:
        return bot.msg(chan, "USAGE: +ageme day month year [prec] [target]")

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
        return bot.msg(chan, "USAGE: +ageme day month year [prec] [target]")

    age = ("%." + prec + "f") % ((time.time() - time.mktime(datetime.date(int(year), int(month), int(day)).timetuple())) / (60 * 60 * 24 * 365.242))

    bot._msg(chan, "*%s is %s years old*" % (nick, age))

"""
Miscellaneous stuff.
"""

from .util.decorators import command, initializer
from .util.data import get_doc
import datetime
import random
import re
from collections import namedtuple

Quote = namedtuple("Quote", ["quote", "author", "extra"])

class QuoteFile(object):
    def __init__(self, quotedb):
        self.internal = quotedb
        self.quotes = []

        self.parse()

    def parse(self):
        data = self.internal.read().split("\n\n")
        for line in data:
            match = re.search(r'(".+")\s+--\s([^(]+)\s*(\(.+\))?', line, flags=re.S)
            if not match:
                raise ValueError("Error while parsing file %s." % (self.internal.name))
            self.quotes.append(Quote(*[i.strip() for i in match.groups()]))

#@initializer
#def initialize_plugin(bot):
#    bot.state.data["quote_db"] = QuoteFile(open("/home/sam/quotes", "r"))

@command("quote", category="misc")
def get_quote(bot, nick, chan, arg):
    """ quote -> get a random quote from the quote db. """
    quote = random.choice(bot.state.data["quote_db"].quotes)
    bot.msg(chan, "%s\n -- %s" % (quote.quote, quote.author))

@command("misc.day_at", category="misc")
def get_weekday_at(bot, nick, chan, arg):
    """ misc.day_at <yyyy-mm-dd> -> get the day of the week at <arg>"""
    if not arg:
        return bot.msg(chan, get_doc())
    arg = arg.split("-")
    year, month, day = (int(item) for item in (arg[0], arg[1], arg[2]))
    time = datetime.datetime(year, month, day)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = days[time.weekday()]
    bot.msg(chan, "The day of the week on \x02%s\x02 was %s" % ("-".join(arg), weekday))


@command("unibarf", short="barf", category="'language'")
def unicode_please(bot, nick, chan, arg):
    """ unibarf -> Return a random number of unicode characters, or <arg> amount. """
    if not arg:
        arg = random.randint(2, 400)
    arg = int(arg)
    startpos = random.randint(1000, 0xFFFF)
    endpos = startpos + arg
    bot.msg(chan, "%s" % ("".join([chr(i) for i in range(startpos, endpos)])))



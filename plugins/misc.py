"""
Miscellaneous stuff.
"""

from .util.decorators import command, initializer
from .util.data import get_doc
import datetime
import random
import re
import requests
from collections import namedtuple

Quote = namedtuple("Quote", ["quote", "author", "extra"])
GITHUBURL_RE = r"(?:https?:\/\/)github.com\/([^\/]+)\/([^\/]+)\/commit\/([a-f0-9]+)"

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

@initializer
def init_plugin(bot):
    bot.state.events.MessageEvent.register(github_url)

def github_url(bot, nick, chan, msg):
    match = re.search(GITHUBURL_RE, msg)
    if not match:
        return

    user, repo, sha = match.groups()

    response = requests.get("https://api.github.com/repos/%s/%s/commits/%s" % (user, repo, sha))
    if (response.status_code != 200):
        return

    data = response.json()
    commit = data['commit']
    
    # Format: [sha] user shortlog +add -sub
    user = commit['committer']['name']
    shortlog = commit['message'].split('\n')[0]
    stats = data['stats']

    bot.msg(chan, "%s %s %s %s %s" %
            (bot.style.color("[%s]" % sha[:7], "gray"),
             bot.style.color(user, "blue"),
             bot.style.color(shortlog, "lblue"),
             bot.style.color("+%s" % (stats['additions']), "green"),
             bot.style.color("-%s" % (stats['deletions']), "red")))


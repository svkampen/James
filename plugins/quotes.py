"""
QuoteDB querying
"""

from .util.decorators import command
import requests
from bs4 import BeautifulSoup as soupify


def fixindent(quoteobj):
    quoteobj = quoteobj.split('\n')
    quoteobj[1] = quoteobj[1].strip()
    return '\n'.join(quoteobj)


@command("quote.get")
def get_quote(bot, nick, target, chan, arg):
    if not arg:
        return bot.msg(chan, "Usage: quote.get #<quotenum>\nExample: quote.get #10")
    quotedb_url = "http://awfulnet.org/quotes/?%s" % (arg.split("#")[1])
    soup = soupify(requests.get(quotedb_url).text)
    quoteobj = soup.find_all("p", {'class': 'quote'})[0].text

    quoteobj = fixindent(quoteobj)

    bot.msg(chan, quoteobj)

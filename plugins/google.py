"""
Google for stuff.
"""
from .util.decorators import command
from .util.data import get_doc
import requests
import re
from html.parser import HTMLParser

def unescape(x):
    return HTMLParser.unescape(None, x)

@command("google", category="internet")
def google(bot, nick, chan, arg):
    """ google <arg> -> Return the google result for <arg> """
    if not arg:
        return bot.msg(chan, get_doc())
    args = arg.split()
    print(args)
    if re.match(r"-\d*", args[0]):
        count = int(args[0][1:])
        query = ' '.join(args[1:])
        print(count, query)
    else:
        count = 1
        query = arg

    url = "http://ajax.googleapis.com/ajax/services/search/web"
    params = {"v": "1.0", "safe": "off", "q":  query}
    data = requests.get(url, params=params)
    data = data.json()

    results = data["responseData"]["results"]

    if not results:
        bot.msg(chan, "%s: No results found." % (nick))

    for i in range(0, count):
        result_url = results[i]["url"]
        result_title = unescape(results[i]["titleNoFormatting"])
        bot.msg(chan, "\x02%s\x02 -- %s" % (result_url, result_title))

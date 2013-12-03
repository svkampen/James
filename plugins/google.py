"""
Google for stuff - and google stuff, like +, etc.
"""
from .util.decorators import command
from .util.data import get_doc
import requests

@command("google", category="internet")
def google(bot, nick, chan, arg):
    """ google <arg> -> Return the google result for <arg> """
    if not arg:
        return bot.msg(chan, get_doc())
    url = "http://ajax.googleapis.com/ajax/services/search/web"
    params = {"v": "1.0", "safe": "off", "q":  arg}
    data = requests.get(url, params=params)
    data = data.json()

    results = data["responseData"]["results"]

    if len(data["responseData"]["results"]) == 0:
        bot.msg(chan, "%s: No results found." % (nick))
    result_url = results[0]["url"]
    result_title = results[0]["titleNoFormatting"]
    bot.msg(chan, "\x02%s\x02 -- %s" % (result_url, result_title))

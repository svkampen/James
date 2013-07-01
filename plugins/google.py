"""
Google for stuff - and google stuff, like +, etc.
"""
from .util.decorators import command
import requests


@command('google')
def google(bot, nick, target, chan, arg):
    """ Return the first google result for <argument>. """
    if not arg:
        return bot.msg(chan, "Usage: google [query]")
    url = 'http://ajax.googleapis.com/ajax/services/search/web'
    params = {'v': '1.0', 'safe': 'off', 'q':  arg}
    data = requests.get(url, params=params)
    data = data.json()

    results = data['responseData']['results']

    if len(data['responseData']['results']) == 0:
        bot.msg(chan, "%s: No results found." % (nick))
    result_url = results[0]['url']
    result_title = results[0]['titleNoFormatting']
    bot.msg(chan, "\x02%s\x02 -- %s" % (result_url, result_title))

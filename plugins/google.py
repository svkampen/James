from .util.decorators import command
import requests

@command('google')
def google(bot, nick, chan, arg):
    if not arg:
        return self._msg(chan, "Usage: google [query]")
    url = 'http://ajax.googleapis.com/ajax/services/search/web'
    params = {'v': '1.0', 'safe': 'off', 'q':  arg}
    data = requests.get(url, params=params)
    data = data.json()

    results = data['responseData']['results']

    if len(data['responseData']['results']) == 0:
        bot._msg(chan, "%s: No results found." % (nick))
    bot._msg(chan, "\x02%s\x02 -- %s" % (results[0]['url'], results[0]['titleNoFormatting']))

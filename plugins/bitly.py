import requests, re
from .util.decorators import command, initializer

def _shorten(bot, url):
    login = bot.data['apikeys']['bit.ly']['user']
    key = bot.data['apikeys']['bit.ly']['key']
    if not url or not re.match("^((https?)?...)(\w+)\.([A-z]+).?[A-z]*", url):
        return "Usage: bitly <VALID url>"
    if not re.match("^(https?)\://.+", url):
        url = 'http://' + url

    jurl = 'https://api-ssl.bitly.com/v3/shorten'
    page = requests.get(jurl, params={'login': login,\
                                   'apiKey': key,\
                                   'longurl': url})

    return page.json()['data']['url']

@initializer
def plugin_initializer(bot):
    bot.data['shortener'] = _shorten

@command('shorten', 'bit.ly', 'bitly')
def bitly(bot, nick, chan, arg):
    data = _shorten(bot, arg)
    bot._msg(chan, data)

"""
Translate module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers


@command('translate')
def translate(bot, nick, target, chan, arg):
    args = arg.split()
    langpair = args[0].replace('-', '|').replace('#', '-')
    word = ' '.join(args[1:])
    url = "http://api.mymemory.translated.net/get"
    params = {'q': word, 'langpair': langpair, 'de': 'sam@tehsvk.net'}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if 'INVALID TARGET LANGUAGE' in data['responseData']['translatedText']:
        return bot.msg(chan, "%s: Invalid target language." % (target))
    print(data)
    bot.msg(chan, "%s: %s" % (target, data['responseData']['translatedText']))

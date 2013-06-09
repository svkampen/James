""" 
Translate module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers

@command('translate')
def translate(bot, nick, chan, arg):
    args = arg.split()
    if args[0].startswith("@"):
        nick = args[0][1:]
        args = args[1:]
    langpair = args[0].replace('-', '|').replace('#', '-')
    word = ' '.join(args[1:])
    url = "http://api.mymemory.translated.net/get"
    params = {'q': word, 'langpair': langpair, 'de': 'sam@tehsvk.net'}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if 'INVALID TARGET LANGUAGE' in data['responseData']['translatedText']:
        return bot.msg(chan, "%s: Invalid target language." % (nick))
    print(data)
    bot.msg(chan, "%s: %s" % (nick, data['responseData']['translatedText']))

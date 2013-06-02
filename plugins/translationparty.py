""" 
Translationparty module.
"""
 
from .util.decorators import command
import requests
from .util.data import www_headers as headers
from threading import Thread
 
@command('translationparty')
def translationparty(bot, nick, chan, arg):
    if not arg:
        return bot.msg(chan, "Usage: translationparty <source>-<target> <times> <sentence>")
    args = arg.split()
    langarg = args[0].split('-')
    langpair = [langarg[0]+"|"+langarg[1], langarg[1]+"|"+langarg[0]]
    try:
        iters = int(args[1])
    except ValueError:
        return bot.msg(chan, "Usage: translationparty <source>-<target> <times> <sentence>")
    if iters > 10:
        return bot.msg(chan, "Maximum iterations is 10!")
    strings = [' '.join(args[2:])]
    url = "http://api.mymemory.translated.net/get"
    for i in range(iters*2):
        params = {'q': strings[i-1], 'langpair': langpair[i%2], 'de': 'sam@tehsvk.net'}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        if 'INVALID TARGET LANGUAGE' in data['responseData']['translatedText']:
            return bot.msg(chan, "%s: Invalid target language." % (nick))
        strings.append(data['responseData']['translatedText'])
        bot.msg(chan, "%s: %d - %s" % (nick, i, strings[i-1]))

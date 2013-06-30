"""
Translationparty module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers
from threading import Thread


@command('translationparty')
def translationparty(bot, nick, target, chan, arg):
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
    tpThread(bot, target, chan, langpair, iters, strings).start()


class tpThread(Thread):
    def __init__(self, bot, target, chan, langpair, iters, strings):
        Thread.__init__(self)
        self.bot = bot
        self.target = target
        self.chan = chan
        self.langpair = langpair
        self.iters = iters
        self.strings = strings

    def run(self):
        url = "http://api.mymemory.translated.net/get"
        for i in range(self.iters*2):
            params = {'q': self.strings[i-1], 'langpair': self.langpair[i % 2], 'de': 'sam@tehsvk.net'}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if 'INVALID TARGET LANGUAGE' in data['responseData']['translatedText']:
                return self.bot.msg(self.chan, "%s: Invalid target language." % (self.target))
            self.strings.append(data['responseData']['translatedText'])
            self.bot.msg(self.chan, "%s: %d - %s" % (self.target, i, self.strings[i-1]))

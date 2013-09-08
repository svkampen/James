"""
Get definitions from google
"""
from .util.decorators import command
from bs4 import BeautifulSoup as soupify
import requests, json
import traceback, random
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

@command('dict', 'dictionary', category='language')
def dict_lookup(bot, nick, chan, arg):
    """ dict <word> -> Dictionary lookup. """
    if not arg:
        return bot.msg(chan, "Usage: dict [query]")

    url = 'http://www.google.com/dictionary/json?callback=dict_api.callbacks.id100&sl=en&tl=en&restrict=pr%2Cde&client=te&q='
    uri = url+urlencode(arg.replace(' ', '+'))
    request = requests.get(uri)

    try:
        data = json.loads(request.text.replace("\\x", "\\u00")[25:-10])
        data = data['webDefinitions'][0]['entries'][0]
        data = data['terms'][0]['text']
        data = soupify(data).getText()
        defs = None

        output = arg + ': ' + data

        output = output.strip()

        if len(output) > 300:
            bot.msg(chan, "%s: %s" % (nick, output[:295]+"[...]"))
        else:
            bot.msg(chan, "%s: %s" % (nick, output))

    except BaseException:
        bot.msg(chan, "No definition found")


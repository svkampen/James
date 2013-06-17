""" 
Insult 'API' (using BeautifulSoup)
"""

from .util.decorators import command, initializer
from .util.data import www_headers as headers
from bs4 import BeautifulSoup as soupify
import re
import requests
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

@command('insult')
def insult(bot, nick, target, chan, arg):
    """ Get an insult. Usage: insult <user> """
    if not arg:
        return bot.msg(chan, insult.__doc__.strip())

    url = 'http://www.randominsults.net/'
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    insult = soup.findAll('i')[0].getText()
    bot._msg(chan, "%s: %s" % (arg, insult))

""" 
Insult 'API' (using BeautifulSoup)
"""
from .util.decorators import command, initializer
from bs4 import BeautifulSoup as soupify
import re
import requests
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

@command('insult')
def insult(bot, nick, chan, arg):
    """ Get an insult. """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible) / JamesIRC'
    }

    nick = arg

    url = 'http://www.randominsults.net/'
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    insult = soup.findAll('i')[0].getText()
    bot._msg(chan, "%s: %s" % (nick, insult))

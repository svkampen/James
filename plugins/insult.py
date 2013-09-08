"""
Insult 'API' (using BeautifulSoup)
"""

from .util.decorators import command
from .util.data import www_headers as headers
from bs4 import BeautifulSoup as soupify
import requests


@command('insult', category='misc')
def insult(bot, nick, chan, arg):
    """ insult <user> -> does this need any help? """
    if not arg:
        return bot.msg(chan, insult.__doc__.strip())

    url = 'http://www.randominsults.net/'
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    insult = soup.findAll('i')[0].getText()
    bot._msg(chan, "%s: %s" % (arg, insult))

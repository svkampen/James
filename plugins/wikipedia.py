""" 
Wikipedia 'API' (using BeautifulSoup)
"""
from .util.decorators import command, initializer
from bs4 import BeautifulSoup as soupify
import re
import requests
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

@initializer
def initialize_plugin(bot):
    """ Initialize this plugin. """
    bot.data['sentence_re'] = re.compile(r"((Dhr\.|Mrs\.|Mr\.)?(.*?)\.)")

@command('wiki')
def wikipedia_get_first_sentence(bot, nick, chan, arg):
    """ Get the first sentence in a wikipedia article. """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible) / JamesIRC'
    }

    arg = arg.replace(" ", "_")
    arg = urlencode(arg)

    url = 'http://en.wikipedia.org/wiki/%s?action=render' % (arg)
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    for s in soup.findAll('table', {'class': 'infobox'}):
        s.extract()
    paragraphs = soup.findAll('p')
    first_paragraph = paragraphs[0].getText()
    first_sentence = bot.data['sentence_re'].match("%s" % (first_paragraph))
    if first_sentence:
        first_sentence = first_sentence.groups()[0]
    else:
        if len(first_paragraph.split(". ")[0]) > 15:
            bot._msg(chan, first_paragraph.split(". ")[0])
            return
    bot._msg(chan, first_sentence)

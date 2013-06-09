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
    bot.state.data['sentence_re'] = re.compile(r"((Dhr\.|Mrs\.|Mr\.)?(.*?)\.)")

@command('wiki')
def wikipedia_get_first_sentence(bot, nick, chan, arg):
    """ Get the first sentence in a wikipedia article. """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible) / JamesIRC'
    }

    if arg.startswith("@"):
        args = arg.split(" ")
        nick = args[0][1:]
        arg = " ".join(args[1:])
    arg = arg.replace(" ", "_")
    arg = urlencode(arg)

    url = 'http://en.wikipedia.org/wiki/%s?action=render' % (arg)
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    for s in soup.findAll('table', {'class': 'infobox'}):
        s.extract()
    paragraphs = soup.findAll('p')
    first_paragraph = paragraphs[0].getText()
    found = bot.state.data['sentence_re'].findall(first_paragraph)
    found = [i[0] for i in found]
    first_sentence = found[0]
    if not first_sentence:
        if len(first_paragraph.split(". ")[0]) > 15:
            bot._msg(chan, "%s: %s -- read more: %s" % (nick, first_paragraph.split(". ")[0], bot.state.data['shortener'](bot, url)))
            return
    bot._msg(chan, "%s: %s -- read more: %s" % (nick, first_sentence+found[1], bot.state.data['shortener'](bot, url.split('?')[0])))

""" 
Wikia 'API' (using BeautifulSoup)
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

@command('wikia')
def wikia_get_first_sentence(bot, nick, target, chan, arg):
    """ Get the first sentence in a wikia article. """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible) / JamesIRC'
    }

    wiki = "uncyclopedia"
    if arg.startswith("@"):
        args = arg.split(" ")
        wiki = args[0][1:]
        arg = " ".join(args[1:])
    arg = arg.replace(" ", "_")
    arg = urlencode(arg)

    url = 'http://%s.wikia.com/wiki/%s?action=render' % (wiki,arg)
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    for s in soup.findAll('table', {'class': 'infobox'}):
        s.extract()
    paragraphs = soup.findAll('p')
    i = 0
    first_paragraph = None
    while first_paragraph == None or len(first_paragraph) < 10:
        first_paragraph = paragraphs[i].getText()
        i += 1
    first_sentence = bot.state.data['sentence_re'].match("%s" % (first_paragraph))
    if first_sentence:
        first_sentence = first_sentence.groups()[0]
    else:
        if len(first_paragraph.split(". ")[0]) > 15:
            bot._msg(chan, "%s: %s -- read more: %s" % (nick, first_paragraph.split(". ")[0], bot.state.data['shortener'](bot, url)))
            return
    bot._msg(chan, "%s: %s -- read more: %s" % (nick, first_sentence, bot.state.data['shortener'](bot, url)))

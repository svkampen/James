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
    if not bot.state.data.get("sentence_re", None):
        return
    else:
        bot.state.data['sentence_re'] = re.compile(r"((Dhr\.|Mrs\.|Mr\.)?(.*?)\.)")


@command('wiki')
def wikipedia_get_first_sentence(bot, nick, target, chan, arg):
    """ Get the first sentence in a wikipedia article. """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible) / JamesIRC'
    }

    arg = arg.replace(" ", "_")
    arg = urlencode(arg)

    root = 'http://en.wikipedia.org/wiki/%s' % (arg)
    url = root+'?action=render'
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    for s in soup.findAll('table', {'class': 'infobox'}):
        s.extract()
    paragraphs = soup.findAll('p')
    first_paragraph = paragraphs[0].getText()
    first_sentence = bot.state.data['sentence_re'].match("%s" % (first_paragraph))
    if first_sentence:
        first_sentence = first_sentence.groups()[0]
    else:
        if len(first_paragraph.split(". ")[0]) > 15:
            bot._msg(chan, "%s: %s -- read more: %s" % (target, first_paragraph.split(". ")[0], bot.state.data['shortener'](bot, root)))
            return
    bot._msg(chan, "%s: %s -- read more: %s" % (target, first_sentence, bot.state.data['shortener'](bot, root)))

from .util.decorators import command, initializer
from bs4 import BeautifulSoup as soupify
import re
import requests
from urllib.request import pathname2url as urlencode

@initializer
def initialize_plugin(bot):
    bot.data['sentence_re'] = re.compile("((Dhr\.|Mrs\.|Mr\.)?(.*?)\.)")

@command('wiki')
def wikipedia_get_first_sentence(bot, nick, chan, arg):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible) / JamesIRC'
    }

    arg = arg.replace(" ", "_")
    arg = urlencode(arg)

    url = 'http://en.wikipedia.org/wiki/%s?action=render' % (arg)
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    [s.extract() for s in soup.findAll('table', {'class': 'infobox'})]
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

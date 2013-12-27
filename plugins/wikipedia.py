"""
Wikipedia "API" (using BeautifulSoup)
"""
from .util.decorators import command, initializer
from bs4 import BeautifulSoup as soupify
from .util.data import www_headers as headers, get_doc
import re
import requests
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode


@initializer
def initialize_plugin(bot):
    """ Initialize this plugin. """
    bot.state.data["sentence_re"] = re.compile(r"(([DM]rs?\.|Miss\.)?(.*?)\.)")


@command("wiki", category="internet")
def wikipedia_get(bot, nick, chan, arg, root=None):
    """ wiki *args -> Get the first two sentences in *args' wikipedia article. """
    if not arg:
        return bot.msg(chan, get_doc())
    term = arg.replace(" ", "_")
    term = urlencode(term)

    if root:
        root = root % term
    else:
        root = ("http://en.wikipedia.org/wiki/%s" % (term))
    url = root+"?action=render"
    response = requests.get(url, headers=headers)

    soup = soupify(response.text)
    for s in soup.findAll("table", {"class": "infobox"}):
        s.extract()
    paragraphs = soup.findAll("p")
    i = 0
    first_paragraph = ""
    while len(first_paragraph) < 20:
        if i < len(paragraphs): 
            first_paragraph = paragraphs[i].getText()
        else:
            return bot.msg(chan, "%s: Sorry. Wikipedia does not have an article for '%s'." % (nick, arg))
        i += 1

    if len(first_paragraph) < 150:
        if i < len(paragraphs): 
            first_paragraph += paragraphs[i].getText()
    first_paragraph = first_paragraph.replace("\n", " ")

    senreg = list(bot.state.data["sentence_re"].finditer("%s" % (first_paragraph)))
    try:
        if len(senreg) > 0:
            sentences = " ".join([x.groups()[0] for x in senreg[:2]])
        else:
            if (len(first_paragraph.split(". ")[0]) + len(first_paragraph.split(". ")[1])) > 32:
                return bot.msg(chan, "%s: %s -- read more: %s" % (nick, " ".join(first_paragraph.split(". ")[:1]), bot.state.data["shortener"](bot, root)))
    except:
        if len(senreg) > 0:
            sentences = senreg[0].groups()[0]
        else:
            if len(first_paragraph.split(". ")[0]) > 15:
                return bot.msg(chan, "%s: %s -- read more: %s" % (nick, first_paragraph.split(". ")[0], bot.state.data["shortener"](bot, root)))
    bot.msg(chan, "%s: %s -- Read more: %s" % (nick, sentences, bot.state.data["shortener"](bot, root)))

@command("ed", category="internet")
def encyclopedia_dramatica(bot, nick, chan, arg):
    """ ed *args -> Get the first two sentences in *args' encyclopedia dramatica article. """
    if not arg:
        return bot.msg(chan, get_doc())
    wikipedia_get(bot, nick, chan, arg, root="https://encyclopediadramatica.es/%s")

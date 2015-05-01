"""
Wikipedia "API" (using BeautifulSoup)
"""
from .util.decorators import command, initializer, cached
from bs4 import BeautifulSoup as soupify
from lxml import etree
from .util.data import www_headers as headers, get_doc, lineify as lines
import re
import time
import requests
import traceback
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

bot = None

def shorten(url):
    return bot.state.data["shortener"](bot, url)

@initializer
def initialize_plugin(irc_bot):
    """ Initialize this plugin. """
    global bot
    bot = irc_bot
    bot.state.data["sentence_re"] = re.compile(r"((?:[DM]rs?\.|Miss\.)?(?:.*?)\.)")
    bot.state.data["wiki_dict"] = {}

@command("wiki", category="internet")
def wikipedia_get(bot, nick, chan, arg, root=None):
    """ wiki <page> -> Get the first two sentences in a wikipedia article. """
    if not arg:
        return bot.msg(chan, get_doc())
    name = arg
    if ' (' in arg:
        name = arg.split()[0]
    term = arg.replace(" ", "_")
    term = urlencode(term)

    url = root or "http://en.wikipedia.org"
    url += ("/w/api.php?action=parse&format=json&prop=text&page=%s&redirects=" % (term))

    response = requests.get(url, headers=headers)
    res = response.json()
    if res.get("error", None):
        return bot.msg(chan, "%s: Error: %s" % (nick, res['error']['info']))

    soup = soupify(res['parse']['text']['*'], "lxml")
    paragraph = soup.find('p')
    url = "http://en.wikipedia.org/wiki/%s"
    htmlurl = url % term

    for i in soup.find_all('b'):
        i.string = "%s" % (bot.hicolor(i.text))
    
    if soup.find("table", id="disambigbox") is not None:
        bot.msg(chan, "%s (%s) points to a disambiguation page." % (arg, shorten(htmlurl)))
        return

    if res['parse'].get('redirects', None):
        if res['parse']['redirects'][0].get("tofragment", None):
            anchor = res['parse']['redirects'][0]['tofragment']
            paragraph = soup.find("span", {"id": anchor}).findNext("p")
            htmlurl = url % (res['parse']['redirects'][0]['to']) + "#%s" % (anchor)
        elif res['parse']['redirects'][0].get("to", None):
            htmlurl = url % (res['parse']['redirects'][0]['to'].replace(" ", "_"))
    sentences = bot.state.data["sentence_re"].findall(paragraph.text)[:2]
    readmore = bot.style.color("⟶ %s\x0f" % (bot.state.data['shortener'](bot, htmlurl)), color="blue")
    text = ''.join(sentences)
    if re.search("\[\d+\]", text):
        text = re.sub("\[\d+\]", "", text)
    output = "%s %s" % (text, readmore)

    bot.msg(chan, '\n'.join(lines(output)))
    time.time()

@cached()
@command("ipa", category="internet")
def get_ipa(bot, nick, chan, arg):
    """ ipa word [lang] -> Get the IPA for a word (in language lang) on wiktionary """
    if not arg:
        return bot.msg(chan, get_doc())
    term = arg.split()[0]
    try:
        lang = arg.split()[1]
    except IndexError:
        lang = "English"

    url = ("http://en.wiktionary.org/w/api.php?format=json&action=parse&prop=text&page=%s&redirects="
        % (term))

    response = requests.get(url, headers=headers)
    data = response.json()

    if data.get("error", None):
        return bot.msg(chan, "%s: Error: %s" % (nick, data['error']['info']))

    soup = soupify(data['parse']['text']['*'])
    try:
        span = soup.find("span", {"id": lang.title()}).findNext("span", {"class": "IPA"})
    except AttributeError:
        traceback.print_exc()
        return bot.msg(chan, "%s: Could not find language in page." % (nick))

    if not span or 'rhymes' in span.find_previous("li").text.lower():
        return bot.msg(chan, "%s: Error: could not find the IPA" % (nick))

    output = "%s: IPA of %s in language %s: %s" % (nick, term, lang, span.text)

    bot.msg(chan, output)
    return output

@command("ed", category="internet")
def encyclopedia_dramatica(bot, nick, chan, arg):
    """ ed *args -> Get the first two sentences in *args' encyclopedia dramatica article. """
    if not arg:
        return bot.msg(chan, get_doc())
    wikipedia_get(bot, nick, chan, arg, root="https://encyclopediadramatica.es")

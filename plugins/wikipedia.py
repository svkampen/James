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
    bot.state.data["sentence_re"] = re.compile(r"((?:[DM]rs?\.|Miss\.|a\.k\.a\.)?(?:.*?)\. )")
    bot.state.data["wiki_dict"] = {}

def wiki_search(term, url=None):
    term = urlencode(term.replace(" ", "_"))
    url = (url or "https://en.wikipedia.org/w/api.php%s") % ("?action=query&prop=pageprops&format=json&generator=search&cllimit=max&gsrsearch=")
    url += term

    data = requests.get(url, headers=headers).json()
    pages = sorted([v for k,v in data['query']['pages'].items()], key=lambda x: x['index'])

    pages = [page for page in pages if not 'disambiguation' in page['pageprops']]
    pages = [{key: t[key] for key in t if key not in ["ns", "index"]} for t in pages]

    return [p['title'] for p in pages]

@command("bwiki", category="internet")
def wiki_get(bot, nick, chan, arg, searchkey=None, api_url=None):
    """ wiki <page> -> Get a summary of a wikipedia article. """
    if not arg:
        return bot.msg(chan, get_doc())

    searchkey = searchkey or arg

    # Get the article name, so we can highlight it later in the function
    article_name = arg
    if (' (' in arg):
        article_name = arg.split()[0]

    term = urlencode(arg.replace(" ", "_"))

    url = (api_url or "https://en.wikipedia.org/w/api.php%s") % ("?action=parse&format=json&prop=text&redirects=&page=")
    url += term

    response = requests.get(url, headers=headers).json()

    if response.get("error", None):
        if response['error']['code'] == "missingtitle":
            # the page we specified does not exist. We'll guess on the basis of search, then.
            return wiki_get(bot, nick, chan, wiki_search(arg, url=api_url)[0], searchkey=arg, api_url=api_url)
        else:
            return bot.msg(chan, "Error: %s" % (response['error']['info']))

    soup = soupify(response['parse']['text']['*'], "lxml")

    # Is the page a disambiguation page? If so, search for the page title and get other pages with similar names

    if soup.find("table", id="disambigbox") is not None:
        return wiki_get(bot, nick, chan, wiki_search(arg, url=api_url)[0], searchkey=arg, api_url=api_url)

    # Get the paragraph and the html url from the soup

    paragraph = get_paragraph(response, soup)
    html_url = get_html_url(response, soup, term)
    print(html_url)

    # First, highlight all of the bold terms in the page
    for i in soup.find_all("b"):
        i.string = "%s" % (bot.hicolor(i.text))

    # Get the sentences
    sentences = ''.join(bot.state.data["sentence_re"].findall(paragraph.text)[:2])

    # Replace footnotes in the sentences
    sentences = re.sub("\[\d+\]", "", sentences)

    # Get other search results
    results = wiki_search(searchkey)[1:4]

    # Get a shortlink
    short_link = bot.state.data["shortener"](bot, html_url)

    output = "%s %s" % (sentences, bot.style.color("\u2192%s" % short_link, "blue"))

    bot.msg(chan, output)

    # other possible pages
    bot.msg(chan, bot.style.color("Did you mean: %s" % (' - '.join(results)), "gray"))

@command("ttdwiki", category="wiki")
def ttdwiki(bot, nick, chan, arg):
    url = "https://wiki.openttd.org/w/api.php%s"
    return wiki_get(bot, nick, chan, arg, api_url=url)


def get_html_url(response, soup, term):
    if 'redirects' in response['parse']:
        if 'tofragment' in response['parse']['redirects'][0]:
            redirect = response['parse']['redirects'][0]
            return "https://en.wikipedia.org/wiki/%s#%s" % (redirect['to'], anchor)
        elif 'to' in res['parse']['redirects'][0]:
            return "https://en.wikipedia.org/wiki/%s" % (redirect['to'].replace(" ", "_"))
    return "https://en.wikipedia.org/wiki/%s" % term

def get_paragraph(response, soup):
    if 'redirects' in response['parse'] and 'tofragment' in response['parse']['redirects'][0]:
        anchor = res['parse']['redirects']['tofragment']
        return soup.find("span", {"id": anchor}).findNext("p")
    return soup.find('p')

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
    readmore = bot.style.color("\u2192 %s\x0f" % (bot.state.data['shortener'](bot, htmlurl)), color="blue")
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
    wikipedia_get(bot, nick, chan, arg, root="http://uncyclopedia.org")

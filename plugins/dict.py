"""
Get definitions from a dictionary source.
"""
from .util.decorators import command
from .util.data import get_doc
from bs4 import BeautifulSoup as soupify
import requests, json

try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

dicts = {}

class Dictionary(object):
    def __init__(self, lang, source="wiktionary"):
        self.language = lang.title()
        if source == "wiktionary":
            self.url = "http://en.wiktionary.org/w/api.php?action=parse&format=json&prop=text&page=%s&redirects="
        else:
            raise NotImplementedError("Only one source (wiktionary) has been implemented.")
    def get(self, word):
        resp = requests.get(self.url % word)
        data = resp.json()
        soup = soupify(data["parse"]["text"]["*"])
        ol = soup.find("span", {"id": self.language}).findNext("ol")
        for item in ol.find_all("ul"):
            item.extract()
        for item in ol.find_all("div", {"class": "thumbcaption"}):
            item.extract()
        definitions = ol.text.strip().split('\n')
        definitions = filter(None, definitions)
        return definitions

dicts["default"] = Dictionary("english")

@command("dict", "dictionary", category="language")
def dict_lookup(bot, nick, chan, arg):
    """ dict <word> [lang] -> Dictionary lookup. """
    if not arg:
        return bot.msg(chan, get_doc())
    args = arg.split()
    if len(args) > 1:
        dicts[args[1]] = Dictionary(args[1])
        defs = dicts[args[1]].get(args[0])
    else:
        defs = dicts["default"].get(arg)
    defs = list(defs)[:5]
    for n, i in enumerate(defs):
        bot.msg(chan, "%d. \x0314%s" % (n+1, i))
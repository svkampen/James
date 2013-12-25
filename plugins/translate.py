"""
Translate module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers
from bs4 import BeautifulSoup as bs

@command("translate", category="language")
def translate(bot, nick, chan, arg):
    """ translate <from>-<to> <snippet> -> translate a text snippet. """
    args = arg.split()
    langpair = args[0].replace("-", "|").replace("#", "-")
    word = " ".join(args[1:])
    url = "http://api.mymemory.translated.net/get"
    params = {"q": word, "langpair": langpair, "de": "sam@tehsvk.net"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if "INVALID TARGET LANGUAGE" in data["responseData"]["translatedText"]:
        return bot.msg(chan, "%s: Invalid target language. See http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes" % (nick))
    if "INVALID SOURCE LANGUAGE" in data["responseData"]["translatedText"]:
        return bot.msg(chan, "%s: Invalid source language. See http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes" % (nick))
    else:
        text =  data["responseData"]["translatedText"]
        text = bs(text).get_text()
        bot.msg(chan, "%s: %s" % (nick, text))

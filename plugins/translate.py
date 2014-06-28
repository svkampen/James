"""
Translate module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers
from html.parser import HTMLParser

def unescape(data):
    return HTMLParser.unescape(None, data)

translate_header = "\x0304Translate│ "

@command("translate", category="language", re="what is (.+?) from (\S+) to (\S+)")
def translate(bot, nick, chan, arg):
    """ translate <from>-<to> <snippet> -> translate a text snippet. """
    if type(arg) == str:
        args = arg.split()
        langpair = args[0].replace("-", "|").replace("#", "-")
        word = " ".join(args[1:])
    else:
        word = arg[0]
        langpair = "%s|%s" % (arg[1], arg[2])
        
    url = "http://api.mymemory.translated.net/get"
    params = {"q": word, "langpair": langpair, "de": "sam@tehsvk.net"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if not data.get("responseData", {}).get("translatedText", []):
        return bot.msg(chan,  "%s\x0314No results." % (translate_header))
    if "INVALID TARGET LANGUAGE" in data["responseData"]["translatedText"]:
        return bot.msg(chan, "%s\x0314Invalid target language. See http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes" % (translate_header))
    elif "INVALID SOURCE LANGUAGE" in data["responseData"]["translatedText"]:
        return bot.msg(chan, "%s\x0314Invalid source language. See http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes" % (translate_header))
    else:
        text =  data["responseData"]["translatedText"]
        text = unescape(text)
        bot.msg(chan, "\x0313%s\x0302 ⟶ \x0314%s" % (word, text))

@command("translate.add", category="language", re="(.+?) = (.+?) from (\S+) to (\S+)")
def translate_add(bot, nick, chan, arg):
    """ translate.add from-to <snip1>-<snip2> -> add a translation. """
    if type(arg) == str:
        args = arg.split()
        langpair = args[0].replace("-", "|").replace("#", "-")
        snip1, snip2 = args[1].split("-")
    else:
        snip1 = arg[0]
        snip2 = arg[1]
        langpair = "%s|%s" % (arg[2], arg[3])

    url = "http://api.mymemory.translated.net/set"
    params = {"seg": snip1, "tra": snip2, "langpair": langpair,
              "de": "sam@tehsvk.net"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data["responseData"] == "OK":
        bot.msg(chan, "Added translation!")
    else:
        bot.msg(chan, "Something went wrong when adding your translation!")
        bot.msg(chan, "%s" % (data))

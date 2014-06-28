"""
Get definitions from urbandictionary
"""
from .util.decorators import command
from .util.data import get_doc, lineify
import requests
import traceback
import random


@command("urban", "urbandictionary", "ud", category="internet")
def urban_lookup(bot, nick, chan, arg):
    """ ud <word> -> look something up on UrbanDictionary. """
    if not arg:
        return bot.msg(chan, "Usage: urban [phrase] [index?]")

    url = "http://www.urbandictionary.com/iphone/search/define"
    args = arg.split()
    params = {"term": " ".join(args[:-1])}
    index = 0
    try:
        index = int(args[-1]) - 1
    except ValueError:
        params = {"term": arg}
    if len(args) == 1:
        params = {"term": arg}
        index = 0
    num = index+1
    if num == 1:
        sign = "\u00B9"
    elif num == 2:
        sign = "\u00B2"
    elif num == 3:
        sign = "\u00B3"
    else:
        sign = chr(0x2070+num)
    request = requests.get(url, params=params)

    data = request.json()
    defs = None
    output = ""
    defs = data["list"]

    if data["result_type"] == "no_results":
        return bot.msg(chan, "\x0314No results for %s\x0314 found, sorry." % (bot.style.color(params["term"], color='pink')))

    output = ("%s%s %s" % (bot.style.color(defs[index]["word"], color="pink"), sign, bot.style.color(defs[index]["definition"], color="grey"))).strip()
    output = " ".join(output.split('\n'))


    if len(output) > 400:
        for i in lineify(output):
            bot.msg(chan, i)

    else:
        bot.msg(chan, "%s" % (output))

@command("urbanrandom", "urbandictionaryrandom", "udr", category="internet")
def urban_random(bot, nick, chan, arg):
    """ urbanrandom -> look a random thing up on UrbanDictionary. """
    word = requests.get("http://api.urbandictionary.com/v0/random").json()["list"][0]["word"]
    urban_lookup(bot, nick, chan, word)

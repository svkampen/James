from .util.decorators import command, initializer
from .util.data import get_doc

import difflib

rfcdata = {}
sections = None
matcher = difflib.SequenceMatcher(None)

@initializer
def plugin_init(bot):
    global sections
    f = open("data/rfc.data", "r").readlines()
    for line in f:
        url, title = line.strip().split(" ", 1)
        rfcdata[title] = url
    sections = list(rfcdata.keys())

def fmatch(title, nmatches=2):
    matches = {}
    for item in sections:
        matcher.set_seqs(title.lower(), item.lower())
        matches[item] = matcher.ratio()
    matches_list = sorted(list(matches.items()), key=lambda x: -x[1])
    return matches_list[:nmatches]

@command('rfcmatch', category='misc')
def rfcmatch(bot, nick, chan, arg):
    """ rfcmatch <item> <n> -> return 1 or <n> RFC section(s) most matching the input string """
    if not arg:
        return bot.msg(chan, get_doc())
    if arg.split()[-1].isdecimal():
        n = int(arg.split()[-1])
    else:
        n = 1
    matches = fmatch(arg, 2)
    mmatches = fmatch(arg+' message', 2)
    combined = sorted(matches+mmatches, key=lambda x: -x[1])
    return [bot.msg(chan, "%s -> %s" % (bot.hicolor(i[0]), rfcdata[i[0]])) for i in combined[:n]]

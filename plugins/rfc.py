from .util.decorators import command, initializer
from .util.data import get_doc

import difflib
import re
import requests
from bs4 import BeautifulSoup

rfc_url = "http://tools.ietf.org/html/"
rfcdata = {}
rfcnumdata = None
rfcs = {}
sections = None
rfcnames = None
matcher = difflib.SequenceMatcher(None)

@initializer
def plugin_init(bot):
    global sections, rfcnumdata, rfcnames
    f = open("data/rfc.data", "r").readlines()
    for line in f:
        url, title = line.strip().split(" ", 1)
        rfcdata[title] = url
    sections = list(rfcdata.keys())
    line = open("data/rfcnum.data", "r").readline()
    rfcnumdata = eval(line.strip())
    f = open("data/rfcs.data", "r").readlines()
    for line in f:
        num = line.split()[0]
        title = line.split(" ", 1)[1].strip()
        rfcs[title] = num
    rfcnames = list(rfcs.keys())


def fmatch(title, items=None, nmatches=2):
    matches = {}
    items = items or sections
    for item in items:
        matcher.set_seqs(title.lower(), item.lower())
        matches[item] = matcher.ratio()
    matches_list = sorted(list(matches.items()), key=lambda x: -x[1])
    return matches_list[:nmatches]

@command('rfc', category='rfc')
def rfcmatch(bot, nick, chan, arg):
    """ rfcmatch <item> <n> -> return 1 or <n> RFC section(s) most matching the input string """
    if not arg:
        return bot.msg(chan, get_doc())
    if arg.split()[-1].isdecimal():
        n = int(arg.split()[-1])
    else:
        n = 1
    matches = fmatch(arg, nmatches=2)
    mmatches = fmatch(arg+' message', nmatches=2)
    for i in mmatches:
        matcher.set_seqs(arg, i[0].rsplit(" ", 1)[0])
        if matcher.ratio() > 0.5:
            matches.append(i)
    matches.sort(key=lambda x: -x[1])
    return [bot.msg(chan, "%s -> %s" % (bot.hicolor(i[0]), rfcdata[i[0]])) for i in matches[:n]]

@command('rfc.num', 'rfc.numeric', category='rfc')
def rfcnum(bot, nick, chan, arg):
    """ rfc.num <numeric> -> return data on an RFC numeric """
    if not arg:
        return bot.msg(chan, get_doc())
    if arg not in rfcnumdata.keys():
        return bot.msg(chan, "%s: %s" % (bot.hicolor(arg), bot.defaultcolor("unknown numeric")))
    bot.msg(chan, rfcnumdata[arg])

@command('rfc.find', category='rfc')
def rfcfind(bot, nick, chan, arg):
    """ rfcfind <name> -> return the RFC URL by name """
    if not arg:
        return bot.msg(chan, get_doc())
    matches = fmatch(arg, rfcnames)
    return [bot.msg(chan, "%s -> %s%s" % (bot.hicolor(i[0]), rfc_url, rfcs[i[0]])) for i in matches]

def rfc_link(bot, nick, chan, msg):
    match = re.search(r"rfc\s*(\d{2,4})", msg, flags=re.I)
    if (not match):
        return

    code = match.group(1)

    rfc_html = requests.get("https://tools.ietf.org/html/rfc%s" % code).text

    soup = BeautifulSoup(rfc_html, "lxml")
    rfc_name = soup.title.text.split(' - ')[1]

    rfc_link = "https://ietf.org/rfc/rfc%s.txt" % code

    output = "%s %s" % (bot.hicolor(rfc_name + '|'), bot.defaultcolor(rfc_link))
    bot.msg(chan, output)

@initializer
def plugin(bot):
    bot.state.events.MessageEvent.register(rfc_link)

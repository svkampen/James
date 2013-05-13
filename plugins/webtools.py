""" 
Webtools - tools for the web.
"""

from .util.decorators import command
from .util.data import www_headers as headers

import requests
import re
from bs4 import BeautifulSoup as soupify

@command('web.title')
def get_title(bot, nick, chan, arg):
    if not arg:
        return bot.msg(chan, "Usage: web.title <url>")
    if not re.match(r"^((https?)?...)(\w+)\.([A-z]+).?[A-z]*", arg):
        return bot.msg(chan, "Usage: web.title <VALID url>")
    if not re.match(r"^(https?)\://.+", arg):
        arg = 'http://' + arg

    url = arg
    data = requests.get(url, headers=headers)
    bot.msg(chan, soupify(data.text).find_all('title')[0].text)


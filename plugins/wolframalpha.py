"""
WolframAlpha 'API' (using proxy)
"""

from .util.decorators import command
import requests, urllib
from .util.data import www_headers as headers
try:
    from urllib.request import pathname2url as urlencode
except:
    from urllib import pathname2url as urlencode

@command('wa')
def proxywa(bot, nick, target, chan, arg): 
    if not arg:
        return bot.msg(chan, "No search term.")
    query = urlencode(arg)
    uri = 'http://tumbolia.appspot.com/wa/%s'
    answer = requests.get(uri % (urllib.parse.quote(query.replace('+', '%2B'))), headers=headers).text.strip('\n').replace(';', '  |  ').replace('\\/', '/')
    if not answer: 
       answer = 'Sorry, no result.'
    bot.msg(chan, "%s: %s" %(target, answer))

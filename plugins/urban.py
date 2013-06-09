""" 
Get definitions from urbandictionary
"""
from .util.decorators import command
import requests

@command('urban', 'urbandictionary', 'ud')
def urban_lookup(bot, nick, chan, arg):
    ''' UrbanDictionary lookup. '''
    if not arg:
        return bot._msg("Usage: urban [phrase]")

    url = 'http://www.urbandictionary.com/iphone/search/define'
    params = {'term': arg}
    request = requests.get(url, params=params)

    data = request.json()
    print(data)
    defs = data['list']
    
    if data['result_type'] == 'no_results':
        return bot._msg(chan, "%s: No definition found for %s." % (nick, arg))

    output = defs[0]['word'] + ': ' + defs[0]['definition']

    output = output.strip()
    output = output.rstrip()
    output = ' '.join(output.split())

    if len(output) > 300:
        tinyurl = bot.state.data['shortener'](bot, defs[0]['permalink'])
        output = output[:output.rfind(' ', 0, 180)] + '...\r\nRead more: %s'\
                 % (tinyurl)
        bot._msg(chan, "%s: %s" % (nick, output))
    
    else:
        bot._msg(chan, "%s: %s" % (nick, output))

@command('urbanrandom', 'urbandictionaryrandom', 'udr')
def urban_random(bot, nick, chan, arg):
    ''' Random UrbanDictionary lookup. '''
    word = requests.get("http://api.urbandictionary.com/v0/random").json()['list'][0]['word']
    urban_lookup(bot, nick, chan, word)

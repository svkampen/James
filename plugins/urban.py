"""
Get definitions from urbandictionary
"""
from .util.decorators import command
import requests
import traceback


@command('urban', 'urbandictionary', 'ud')
def urban_lookup(bot, nick, target, chan, arg):
    ''' UrbanDictionary lookup. '''
    if not arg:
        return bot.msg(chan, "Usage: urban [phrase] [index?]")

    url = 'http://www.urbandictionary.com/iphone/search/define'
    args = arg.split()
    params = {'term': ' '.join(args[:-1])}
    index = 0
    try:
        index = int(args[-1]) - 1
    except ValueError:
        params = {'term': arg}
    if len(args) == 1:
        params = {'term': arg}
        index = 0
    request = requests.get(url, params=params)

    data = request.json()
    defs = None
    output = ""
    try:
        defs = data['list']

        if data['result_type'] == 'no_results':
            return bot.msg(chan, failmsg() % (nick, params['term']))

        output = defs[index]['word'] + ' [' + str(index+1) + ']: ' + defs[index]['definition']
    except:
        traceback.print_exc()
        return bot._msg(chan, failmsg() % (nick, params['term']))

    output = output.strip()
    output = output.rstrip()
    output = ' '.join(output.split())

    if len(output) > 300:
        tinyurl = bot.state.data['shortener'](bot, defs[index]['permalink'])
        output = output[:output.rfind(' ', 0, 180)] + '...\r\nRead more: %s'\
            % (tinyurl)
        bot.msg(chan, "%s: %s" % (target, output))

    else:
        bot.msg(chan, "%s: %s" % (target, output))

def failmsg():
    import random
    return random.choice([
        "%s: No definition found for %s.",
        "%s: The heck is '%s'?!",
        "%s: %s. wut.",
        "%s: %s? I dunno...",
        "%s: Stop searching weird things. What even is '%s'?",
        "%s: Computer says no. '%s' not found.",
        "*sigh* someone tell %s what '%s' means",
        "%s: This is a family channel. Don't look up '%s'",
        "%s: Trust me, you don't want to know what '%s' means.",
        "%s: %s [1]: Something looked up by n00bs.",
        "%s: %s [1]: An obscure type of fish.",
        "No %s, no '%s' for you.",
        "Shh %s, nobody's meant to know about '%s'...",
        "Really %s? %s?"])

@command('urbanrandom', 'urbandictionaryrandom', 'udr')
def urban_random(bot, nick, target, chan, arg):
    ''' Random UrbanDictionary lookup. '''
    word = requests.get("http://api.urbandictionary.com/v0/random").json()['list'][0]['word']
    urban_lookup(bot, nick, target, chan, word)

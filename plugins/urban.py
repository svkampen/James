from util.decorators import command
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
    return None
    defs = data['list']
    
    if data['result_type'] == 'no_results':
        bot._msg(nick, "No definition found.")

    output = defs[0]['word'] + ': ' + defs[0]['definition']

    output = output.strip()
    output = output.rstrip()
    output = ' '.join(output.split())

    if len(output) > 200:
        tinyurl = bot.data['shortener'](bot, defs[0]['permalink'])
        output = output[:output.rfind(' ', 0, 180)] + '...\r\nRead more: %s' % (tinyurl)
        bot._msg(chan, "%s: %s" % (nick, output))
    
    else:
        bot._msg(chan, "%s: %s" % (nick, output))


""" 
Weather module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers
from threading import Thread, Event

@command('whereis')
def whereis(bot, nick, chan, arg):
    args = arg.split()
    if args[0].startswith("@"):
        nick = args[0][1:]
        args = args[1:]
    locn = ' '.join(args)
    url = "http://api.openweathermap.org/data/2.5/find"
    params = {'units': 'metric', 'mode': 'json', 'type': 'like', 'q': locn}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    print(data)
    if data['cod'] != '200' or data['count'] == 0:
        return bot.msg(chan, "%s: Invalid location." % (nick))
    names = []
    for entry in data['list']:
        name = u"%s: %s" % (entry['name'], entry['sys']['country'])
        if name != '':
            names.append(name)
    bot.msg(chan, ", ".join(names))

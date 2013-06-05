
""" 
Weather module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers
from threading import Thread, Event

@command('weather')
def weather(bot, nick, chan, arg):
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
    WeatherThread(bot, chan, data).start()

class WeatherThread(Thread):
    def __init__(self, bot, chan, data):
        Thread.__init__(self)
        self.bot = bot
        self.chan = chan
        self.data = data

    def run(self):
        for entry in self.data['list']:
            name = u"%s, %s" % (entry['name'], entry['sys']['country'])
            main = entry['main']
            # This is nesty
            try:
                feel = "%d%% cloudy, %s" % (main['clouds']['all'], main['weather']['description'])
            except:
                try:
                    feel = "%s" % (main['weather']['description'])
                except:
                    feel = ''
            try:
                temp = "Temperature is %d°C right now. Max: %d°C, Min: %d°C." % (main['temp'], main['temp_min'], main['temp_max'])
            except:
                try:
                    temp = "Temperature is %d°C right now." % (main['temp'])
                except:
                    temp = ''
            try:
                misc = "Pressure is at %d hPa. Humidity is %d%%. Wind going by %d° at %d m/s" % (main['pressure'], main['humidity'], main['wind']['deg'], main['wind']['speed'])
            except:
                try:
                    misc = "Wind going by %d° at %d m/s" % (main['wind']['deg'], main['wind']['speed'])
                except:
                    misc = ''
            for line in (temp, misc, feel):
                if line != '':
                    self.bot.msg(self.chan, "%s: %s" % (name, line))
            Event().wait(8)


""" 
Weather module.
"""

from .util.decorators import command
import requests
from .util.data import www_headers as headers
from threading import Thread

@command('weather')
def weather(bot, nick, chan, arg):
    args = arg.split()
    if args[0].startswith("@"):
        nick = args[0][1:]
        args = args[1:]
    locn = ' '.join(args[1:])
    url = "http://api.openweathermap.org/data/2.5/find?units=metric&mode=json&type=like&q="
    url += urllib.quote(locn, safe='')
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data['count'] == 0:
        return bot.msg(chan, "%s: Invalid location." % (nick))
    print(data)
    WeatherThread(bot, chan, data).start()

class WeatherThread(Thread):
    def __init__(self, bot, chan, data):
        Thread.__init__(self)
        this.bot = bot
        this.chan = chan
        this.data = data

    def run(self):
        for entry in this.data['list']:
            name = u"%s, %s" % (entry['name'], entry['sys']['country'])
            main = entry['main']
            temp = "Temperature is %d°C right now. Max: %d°C, Min: %d°C." % (main['temp'], main['temp_min'], main['temp_max'])
            pressure = "Pressure is at %d hPa. %d hPa at Sea level, %d hPa at Ground level." % (main['pressure'], main['sea_level'], main['grnd_level'])
            misc = "Humidity is %d%%. Wind going by %d° at %d m/s" % (main['humidity'], main['wind']['deg'], main['wind']['speed'])
            feel = "%d%% cloudy, %s" % (main['clouds']['all'], main['weather']['description'])
            this.bot.msg(this.chan, "%s: %s" % (name, temp))
            this.bot.msg(this.chan, "%s: %s" % (name, pressure))
            this.bot.msg(this.chan, "%s: %s" % (name, misc))
            this.bot.msg(this.chan, "%s: %s" % (name, feel))

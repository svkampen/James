""" 
plugin for reddit stuff.
"""

from .util.decorators import command, initializer
from .util.data import www_headers as headers
from .util.threads import Ticker
import time
import requests

class RedditTicker(Ticker):
    def __init__(self, bot, subreddit, chan_to_msg=None):
        if not chan_to_msg:
            chan_to_msg = '#%s' % (subreddit)
        self.chan_to_msg = chan_to_msg
        self.last_post_id = 'None'
        self.bot = bot
        self.subreddit = subreddit
        self.url = 'http://reddit.com/r/%s/new.json' % (subreddit)
        super().__init__(self.url, sleeptime=30, hooks=[self.respond])
        
    def respond(self, response):
        try:
            data = response.json()['data']['children']
        except BaseException:
            print("Error decoding object from json data. Possible error in subreddit.")
        if self.loops != 1:
            data = data[:1]
        for item in data:
            if item['data']['id'] != self.last_post_id:
                data_title = item['data']['title']
                permalink = item['data']['permalink']
                data_url = self.bot.data['shortener'](self.bot, 'http://reddit.com'+permalink)
                self.bot.msg(self.chan_to_msg, "[\x02r/%s\x02] %s - \x02%s\x02" \
                             % (self.subreddit, data_title, data_url))
                time.sleep(2)
            else:
                break
        self.last_post_id = data[0]['data']['id']
        
        

@command('reddit.last')
def reddit_get_last_post(bot, nick, chan, arg):
    if not arg:
        return bot.msg(chan, "Usage: reddit.last <subreddit>")
    url = 'http://reddit.com/r/%s/new.json' % (arg)
    response = requests.get(url, headers=headers)

    data = response.json()['data']['children'][0]['data']
    data_title = data['title']
    data_url = data['url']

    data_url = bot.data['shortener'](bot, data_url)
    bot.msg(chan, "[\x02r/%s\x02] %s - \x02%s\x02" % (arg, data_title, data_url))

@command('reddit.hot')
def reddit_get_hot_post(bot, nick, chan, arg):
    if not arg:
        return bot.msg(chan, "Usage: reddit.hot <subreddit>")
    url = 'http://reddit.com/r/%s/hot.json' % (arg)
    response = requests.get(url, headers=headers)
    
    data = response.json()['data']['children'][0]['data']
    data_title = data['title']
    data_url = bot.data['shortener'](bot, data['url'])
    
    bot.msg(chan, "[\x02r/%s\x02] %s - \x02%s\x02" % (arg, data_title, data_url))

@initializer
def plugin_initializer(bot):
    bot.data['tickers'] = []
    globals()['bot'] = bot

@command('reddit.ticker.add_hook')
def reddit_add_hook(bot, nick, chan, arg):
    if not arg:
        return bot.msg(chan, "Usage: reddit.ticker.add_hook <subreddit>")

    bot.data['tickers'].append(RedditTicker(bot, arg, chan_to_msg=chan))
    bot.data['tickers'][-1].setDaemon(True)
    bot.data['tickers'][-1].start()
    bot.msg(chan, "Added %s" % (bot.data['tickers'][-1]))

@command('reddit.ticker.remove_hook')
def reddit_del_hook(bot, nick, chan, arg):
    for ticker in bot.data['tickers']:
        if ticker.subreddit == arg:
            ticker.running = False
            bot.msg(chan, "Removed ticker %s" % (ticker))

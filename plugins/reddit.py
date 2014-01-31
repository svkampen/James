"""
plugin for reddit stuff.
"""

from .util.decorators import command, initializer
from .util.data import www_headers as headers, get_doc
from .util.threads import Ticker
import time
import requests
from collections import deque


class RedditTicker(Ticker):
    def __init__(self, bot, subreddit, chan_to_msg=None):
        if not chan_to_msg:
            chan_to_msg = "#%s" % (subreddit)
        self.chan_to_msg = chan_to_msg
        self.last_post_id = deque(maxlen=5)
        self.bot = bot
        self.subreddit = subreddit
        self.url = "http://reddit.com/r/%s/new.json" % (subreddit)
        super().__init__(self.url, sleeptime=30, hooks=[self.respond])
        self.name = subreddit

    def respond(self, response):
        try:
            data = response.json()["data"]["children"]
        except BaseException:
            print("Error decoding object from json data. Possible error in subreddit.")
        if self.loops != 1:
            data = data[:1]
        for item in data:
            if item["data"]["id"] not in self.last_post_id:
                data_title = item["data"]["title"]
                #permalink = item["data"]["permalink"]
                data_url = "http://redd.it/%s" % (item["data"]["id"])
                self.bot.msg(self.chan_to_msg, "[\x02r/%s\x02] %s - \x02%s\x02"
                             % (self.subreddit, data_title, data_url))
                time.sleep(2)
            else:
                break
        self.last_post_id.append(data[0]["data"]["id"])


@command("reddit.last", category="social")
def reddit_get_last_post(bot, nick, chan, arg):
    """ reddit.last <subreddit> -> Get the last post of a subreddit on reddit. """
    if not arg:
        return bot.msg(chan, get_doc())
    url = "http://reddit.com/r/%s/new.json" % (arg)
    response = requests.get(url, headers=headers)

    data = response.json()["data"]["children"][0]["data"]
    data_title = data["title"]
    data_url = data["url"]

    data_url = bot.state.data["shortener"](bot, data_url)
    bot.msg(chan, "[\x02r/%s\x02] %s - \x02%s\x02" % (arg, data_title, data_url))


@command("reddit.hot", category="social")
def reddit_get_hot_post(bot, nick, chan, arg):
    """ reddit.hot <subreddit> -> Get the hottest post on a subreddit. """
    if not arg:
        return bot.msg(chan, get_doc())
    url = "http://reddit.com/r/%s/hot.json" % (arg)
    response = requests.get(url, headers=headers)

    data = response.json()["data"]["children"][0]["data"]
    data_title = data["title"]
    data_url = bot.state.data["shortener"](bot, data["url"])

    bot.msg(chan, "[\x02r/%s\x02] %s - \x02%s\x02" % (arg, data_title, data_url))


@initializer
def plugin_initializer(bot):
    bot.state.data["threads"] = []
    globals()["bot"] = bot


@command("reddit.ticker.add_hook", category="automation")
def reddit_add_hook(bot, nick, chan, arg):
    """ reddit.ticker.add_hook <subreddit> -> Add a ticker for a hook. """
    if not arg:
        return bot.msg(chan, get_doc())

    bot.state.data["threads"].append(RedditTicker(bot, arg, chan_to_msg=chan))
    bot.state.data["threads"][-1].setDaemon(True)
    bot.state.data["threads"][-1].start()
    bot.msg(chan, "Added %s" % (bot.state.data["threads"][-1]))


@command("reddit.ticker.remove_hook", category="automation")
def reddit_del_hook(bot, nick, chan, arg):
    """ reddit.ticker.remove_hook <subreddit> -> Delete a reddit ticker. """
    for ticker in bot.state.data["threads"]:
        if ticker.subreddit == arg:
            ticker.running = False
            ticker.join()
            bot.state.data["threads"].pop(ticker)
            bot.msg(chan, "Removed ticker %s" % (ticker))

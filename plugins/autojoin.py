"""
Autojoin.py - Autojoining.
"""

from .util.decorators import initializer


def autojoin(bot, *args, **kwwargs):
    if bot.state.data.get('autojoin_channels', None):
        for channel in bot.state.data['autojoin_channels']:
            bot._send("JOIN :%s" % (channel))


@initializer
def register_events(bot):
    bot.state.events['WelcomeEvent'].register(autojoin)

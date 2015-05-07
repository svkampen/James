"""
Shorter url-shortener plugin
Uses v.gd.
"""

from .util.decorators import command, initializer
import re
import requests

def _shorten(bot, url):
    if not url or not re.match(r"^((https?)?...)(\S+)\.([A-z]+).?[A-z]*", url):
        return "Usage: shorten <VALID url>"
    if not re.match(r"^(https?)\://.+", url):
        url = "http://" + url

    params = {"format": "simple", "url": url}
    return requests.get("http://v.gd/create.php", params=params).text

@initializer
def plugin_initializer(bot):
    """ Initialize this plugin. """
    # bot.state.data["shortener"] = _shorten
    pass

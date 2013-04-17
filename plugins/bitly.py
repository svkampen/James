def _shorten(self, url):
    if not url:
        return "Usage: bitly <url>"
    if not url.startswith("http"):
        arg = 'http://' + arg

    jurl = 'http://api.bit.ly/shorten?version=2.0.1&%s'

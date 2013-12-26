"""
IMDB plugin
"""

from .util.decorators import command
from .util.data import get_doc

import requests

@command("imdb", category="internet")
def get_imdb(bot, nick, chan, arg):
	b, u = (bot.style.bold, bot.style.underline)
	base_url = "http://mymovieapi.com/?title=%s&type=json&tech=1" % arg.replace(" ", "+")
	data = requests.get(base_url).json()
	movie = data[0]
	
	title = b(u("%s (%s)" % (movie.get("title"), movie.get("year", "2013"))))
	rating = movie.get("rating", "unknown")
	genre = ', '.join(movie.get("genres", ["unknown"]))
	length = movie.get("runtime", ['unknown'])[0]
	plot = movie.get("plot_simple", 'unknown')

	output = "%s: %s: %s %s: %s %s: %s %s: %s" % (title, u("Rating"), rating,
		u("Genre"), genre, u("Length"), length, u("Plot"), plot)

	bot.msg(chan, output)
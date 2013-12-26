"""
IMDB plugin
"""

from .util.decorators import command
from .util.data import get_doc

import requests

@command("imdb", category="internet")
def get_imdb(bot, nick, chan, arg):
	b, u = (bot.style.bold, bot.style.underline)
	base_url = "http://mymovieapi.com/?title=%s&type=json" % arg
	data = requests.get(base_url).json()
	movie = data[0]
	
	title = b(u("%s (%s)" % (movie.get("title"), movie.get("year", "2013"))))
	rating = movie.get("rating", "0.0")
	genre = ', '.join(movie.get("genres", []))
	length = movie.get("runtime", [''])[0]
	plot = movie.get("plot_simple", '')

	output = "%s: %s: %s %s: %s %s: %s %s: %s" % (title, u("Rating"), rating,
		u("Genre"), genre, u("Length"), length, u("Plot"), plot)

	bot.msg(chan, output)
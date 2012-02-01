#!/usr/bin/python
# RUINBot version 0.2 DEVEL TESTING OPERA DERPY CATNIP STERLING POUND
# aka RUINBot Codename Opera
# 
# Some of the main code copied from Kitn (as there is no Oyoyo documentation)
# That code (C) 2011 Amber Yust =)
# 
# https://github.com/svkampen/RUINBot/wiki/About
#

from oyoyo.client import IRCClient, IRCApp
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

import functools # Again, yay Amber.

from urlparse import urlparse

from BeautifulSoup import BeautifulSoup as soup

import logging
import re
import yaml # You need PyYAML for this.
import sys
import sqlite3
import traceback

import random

logging.basicConfig(level=logging.INFO)
config = None
app = None

def admin_only(f):
        @functools.wraps(f)
        def wrapper(self, nick, chan, arg):
                if nick == 'svkampen!svkampen@Srs.Face':
                        return f(self, nick, chan, arg)
                elif nick == 'Nagah!max@Acael.us':
                	return self._msg(chan, "NO ADMEEN FOR YU!")
                else:
                        return self._msg(chan, "Permission Denied.")
        return wrapper

class RUINHandler(DefaultCommandHandler):

    def __init__(self, *args, **kwargs):
	super(RUINHandler, self).__init__(*args, **kwargs)
	
	self.COMMAND_RE = re.compile(r"^(?:%s:\s+|%s)(\w+)(?:\s+(.*))?$" % (self.client.nick, re.escape(config['sigil'])))

		# URLs

		self.URL_RE = re.compile(r"""
				\b
				(
					(https?://|www\.)    
					([a-zA-Z0-9-]+\.)+   # domain segments
					[a-zA-Z]{2,4}        # TLD
					
					# We don't require 'nice' URLs to have a path (/ can be implied)
				|
					# URLs that don't start with a 'nice' prefix
  					([a-zA-Z0-9-]+\.)+   # domain segments
					[a-zA-Z]{2,4}        # TLD
					(?=/)                # These URLs are required to at least have a /
				)
				(
					/
					(
						\([^\s()]+\)     # Allow paired parens
					|
						[^\s()]+         # Normal URL content (no parens)
					)*
				)?
			""", re.X)


    def welcome(self, nick, chan, msg):
        # I had a lot of trouble doing this, so most of the code is copied from Amber (as this seems a great way)
        """Trigger on-login actions via the WELCOME event."""
        s = config['servers'][self.client.host]
        # If an auth is specified, use it.
        auth = s.get('auth')
        if auth:
            try:
                self._msg(auth['to'], auth['msg'])
            except KeyError:
                logging.error('Authentication info for %s missing "to" or "msg", skipping.' % self.client.host)
		# If default channels to join are specified, join them.
                channels = s.get('channels', ())
                for channel in channels:
                    helpers.join(client, channel)		
                # If server-specific user modes are specified, set them.
                modes = s.get('modes')
                if modes:
                    client.send('MODE', s['nick'], modes)
		logging.info("Completed connection actions for %s." % self.client.host)



    def privmsg(self, nick, chan, msg):
        logging.info("Message received: [%s] <%s>: %s " % (chan, nick, msg))     
        self.parser(nick, chan, msg)

    def parser(self, nick, chan, msg):

        # Match the cmdchar or RUINBot's nick (@Amber I love you. This is epic. I love your code 
        m = self.COMMAND_RE.match(msg)
	    if m:
	        cmd = m.group(1)
		arg = m.group(2)
		cmd_func = '_cmd_%s' % cmd.upper()
		if hasattr(self, cmd_func):
		    try:
			getattr(self, cmd_func)(nick, chan, arg)
		    except:
		        logging.error("Exception while attempting to process command '%s'" % cmd, exc_info=True)
			# Don't try to parse a URL in a recognized command
	            return
		else:
		    logging.warning('Unknown command "%s".' % cmd)

	m = self.URL_RE.search(msg)
	if m:
	    logging.info("Found URL in %s: %s" % (chan, m.group()))
	    self._url_announce(chan, m.group())



    # Commandohs.

	def _url_announce(self, chan, url):
		# Amber.
		"""Announce the info for a detected URL in the channel it was detected in."""
		try:
			if not url.startswith("http"):
				url = "http://%s" % url
			orig_domain = urlparse(url).netloc
			result = urllib2.urlopen(url, timeout=5)
			final_url = result.geturl()
			final_domain = urlparse(final_url).netloc
			report_components = []
			if orig_domain != final_domain:
				report_components.append("[%s]" % final_domain)
			if result.info().getmaintype() == 'text':
				# Try parsing it with BeautifulSoup
				parsed = soup(result.read())
				title_tag = parsed.find('title')
				if title_tag:
					title_segments = re.split(r'[^a-z]+', title_tag.string[:100].lower())
					title_segment_letters = (
							''.join(L for L in segment.lower() if L in string.lowercase)
							for segment in title_segments
						)
					title_segment_letters = [s for s in title_segment_letters if s]
					f = final_url.lower()
					title_segments_found = [s for s in title_segment_letters if s in f]
					found_len = len(''.join(title_segments_found))
					total_len = len(''.join(title_segment_letters))

					if found_len < 0.6 * total_len:
						logging.info("Reporting title '%s' (found: %s, total: %s)" % (
							title_tag.string[:100], found_len, total_len))
						report_components.append('"%s"' % title_tag.string[:100])
					else:
						logging.info("Not reporting title '%s' (found: %s, total: %s)" % (
							title_tag.string[:100], found_len, total_len))
						
			# Only announce the url if something caught our attention
			if report_components:
				self._msg(chan, "Link points to %s" % ' - '.join(report_components))

		except urllib2.URLError:
			logging.info("URLError while retrieving %s" % url, exc_info=True)
		except ValueError:
			logging.warning("Unable to examine URL %s" % url, exc_info=True)


    def cmd_ABOUT(self, nick, chan, arg):
        self._msg(chan, "Ohai! I am RUINBot. Some/Most of my code is forked off Aiiane (Amber Yust)'s Kitn, but we shall be using own code soon =)")
        self._msg(chan, "My owner is svkampen. For more info, go to https://github.com/svkampen/RUINBot/wiki/About")

    def _cmd_CHOOSE(self, nick, chan, arg):
	"""choose - Given a set of items, pick one randomly."""
	usage = lambda: self._msg(chan, "Usage: choose <item> <item> ...")
	items = arg.split()
	if not items:
	    return usage()
	else:
            self._msg(chan, "%s: %s" % (nick.split('!')[0], random.choice(items)))

    @admin_only
    def cmd_JOIN(self, nick, chan, arg):
        self._msg(chan, "Joining channel %s on request of %s." % (arg, nick))
        helpers.join(self.client, arg)
        logging.info("[JOIN] %s by %s" % (arg, nick))

    @admin_only
    def cmd_PART(self, nick, chan, arg):
        self._msg(chan, "Parting channel %s on request of %s." % (arg, nick))
        helpers.part(self.client, arg)
        logging.info("[PART] %s by %s" % (arg, nick))


    def cmd_FACTOID(self, nick, chan, arg):	
	args = arg.split()

	if args[0] == "add":
	    word = args[1]
	    factoid = ' '.join(args[2:])


            db.execute("INSERT INTO factoids (trigger, factoid) VALUES('%s', '%s')" % (word, factoid))
	    r_id = result.lastrowid
	    self._msg(chan, "%s: Factoid Added =) (ID: %s)" % (nick, r_id))

	    logging.info("[FACTOIDS] ADDED REFERENCE %s | %s (Nick: %s)" % (word, factoid, nick))

	if args[0] == "list":
	    
	    db.execute("SELECT * FROM factoids")
	    self._msg(chan, db.fetchall())
	    
	    logging.info("[FACTOIDS] Factoids listed.!")

	if args[0] == "listnr":
	    
	    factoidID = args[1]

	    db.execute("SELECT * FROM factoids WHERE ID = '%s'" % factoidID)
	    self._msg(chan, db.fetchall())
	    
	    logging.info("[FACTOIDS] Listed %s" % id)

	def _cmd_XKCD(self, nick, chan, arg):
		# My code, even though amber's is almost the same.
		try:
			comic = int(arg)
			comic_json_uri = "http://xkcd.com/%d/info.0.json" % comic
		except (TypeError, ValueError):
			comic_json_uri = "http://xkcd.com/info.0.json"
		try:
			data = urllib2.urlopen(comic_json_uri, timeout=3)
			xkcd_json = json.load(data)
			self._msg(chan, "xkcd #%d: %s <http://xkcd.com/%d/>" % (
				xkcd_json['num'], xkcd_json['title'], xkcd_json['num'],
			))
		except urllib2.URLError:
			self._msg(chan, "Comic lookup failed (Comic #%s)" % comic)


    def cmd_TEEHEE(self, nick, chan, arg):
	self._msg(chan, "Ha. Ha. Ha. Ha. Stayin' Alive!")
        logging.info("[CMDS] Executed.")

    def cmd_RUINSITE(self, nick, chan, arg):
	self._msg(chan, "Our site: http://ruincommunity.net/")
        self._msg(chan, "Donate: http://ruincommunity.net/donate")

    def cmd_CMDS(self, nick, chan, arg):
	self._msg(chan, "Commands: [@join]*, [@part]*, [@about], [@teehee], [@ruinsite]")
        self._msg(chan, "* = Owner Only")

    def _msg(self, chan, msg):
        helpers.msg(self.client, chan, msg)

if __name__ == '__main__':
	
        with open('config.yaml') as f:
		config = yaml.safe_load(f)
	
	db = sqlite3.connect(config['db']['path'])
        db.execute("""CREATE TABLE IF NOT EXISTS factoids (id INTEGER PRIMARY KEY AUTOINCREMENT, trigger TEXT, factoid TEXT)""")
	db.commit()
	
	

	app = IRCApp()
	clients = {}
	for server, conf in config['servers'].iteritems():
		client = IRCClient(
			RUINHandler,
			host=server,
			port=conf['port'],
			nick=conf['nick'],
			real_name=conf['name'],
		)
		clients[server] = client
		app.addClient(client)
	app.run()

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

import logging
import re
import yaml # You need PyYAML for this.
import sys

import traceback

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
        
        self.cmdparse(nick, chan, msg)

    def cmdparse(self, nick, chan, msg):
        # Match the cmdchar or RUINBot's nick (@Amber I love you. This is epic. I love your code =)
        cmd_inmsg = re.compile(r"^(?:%s:\s+|%s)(\w+)(?:\s+(.*))?$" % ( self.client.nick, re.escape(config['cmdchar']), ))

        m = cmd_inmsg.match(msg)
        if m:
            cmd = m.group(1)
            arg = m.group(2)
            cmd_func = 'cmd_%s' % cmd.upper()
            if hasattr(self, cmd_func):
                try:
                    getattr(self, cmd_func)(nick, chan, arg)
                except:
                    logging.error("Exception while processing command '%s' D=") % (cmd)
            else:
                logging.warning('Unknown command "%s".' % (cmd))

    # Commandohs.
    def cmd_ABOUT(self, nick, chan, arg):
        self._msg(chan, "Ohai! I am RUINBot. Some/Most of my code is forked off Aiiane (Amber Yust)'s Kitn, but we shall be using own code soon =)")
        self._msg(chan, "My owner is svkampen. For more info, go to https://github.com/svkampen/RUINBot/wiki/About")

    @admin_only
    def cmd_JOIN(self, nick, chan, arg):
	usage = lambda: self._msg(chan, "Usage: join <chan>")
        
        self._msg(chan, "Joining channel %s on request of %s." % (arg, nick))
        helpers.join(self.client, arg)
        logging.info("[JOIN] %s by %s" % (arg, nick))

    @admin_only
    def cmd_PART(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: part <chan>")
        self._msg(chan, "Parting channel %s on request of %s." % (arg, nick))
        helpers.part(self.client, arg)
        logging.info("[PART] %s by %s" % (arg, nick))

    def cmd_FACT(self, nick, chan, arg):
	usage = lambda: self._msg(chan, "Usage: fact <operation> <trigger> <factoid> | Adds factoids =)")	

	args = arg.split()
        
	global id

	if args[0] == "add":

            id = id++
	    word = args[1]
	    factoid = ' '.join(args[2:])


            db.execute("INSERT INTO mediarefs VALUES('%s', '%s', '%s')"" % (id, word, factoid)
	    self._msg(chan, "%s: MediaReference Added =) (ID: %s)" % (nick, id))

	    logging.info("[MediaRefs] ADDED REFERENCE %s | %s (Nick: %s)" % (word, factoid, nick))

	if args[0] == "list":
	    
	    db.execute("SELECT * FROM mediarefs")
	    self._msg(chan, db.fetchall())
	    
	    logging.info("[MediaRefs] LISTED!")

	if args[0] == "listnr":
	    
	    db.execute("SELECT * FROM mediarefs WHERE ID ='%s'"" % (id))
	    self._msg(chan, db.fetchall())
	    
	    logging.info("[MediaRefs] Listed %s" %s id)

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
        db.execute("""CREATE TABLE IF NOT EXISTS mediarefs (id INTEGER, trigger TEXT, factoid TEXT)""")
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

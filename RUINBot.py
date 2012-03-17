#!/usr/bin/env python
#
# RUINBot version 12.3.17
# Build Date: 17032012
# 
# (C) 2012 Sam van Kampen
#
# Some of the main code copied from Kitn (as there is no Oyoyo documentation)
# That code (C) 2011 Amber Yust =)
# 
# https://github.com/svkampen/RUINBot/wiki/About
#

from oyoyo.client import IRCClient, IRCApp
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

import json, urllib2, tweepy, urllib
from time import strftime
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
    
class RUINHandler(DefaultCommandHandler):

    def __init__(self, *args, **kwargs):
        '''Handles initial actions.'''
        super(RUINHandler, self).__init__(*args, **kwargs)
        self.COMMAND_RE = re.compile(r"^(?:%s:\s+|%s)(\w+)(?:\s+(.*))?$" % (self.client.nick, re.escape(config['cmdchar'])))
        self.operedup = None
        self.messages = dict()
        self.messages['lm'] = ""
        self.admins = dict()
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
        botnick = self.client.nick
        botnick = botnick.upper()
        if chan.upper() == botnick:
            self.pm = 1
            if not msg.startswith(config['cmdchar']):
                nick = nick.split('!')
                nick = nick[0]
                self._msg(nick, "Unknown command..")
        else:
            self.pm = 0
        self.messages['slm'] = self.messages['lm']
        self.messages['lm'] = msg     
        self.parser(nick, chan, msg)

    def join(self, nick, chan):
        nick = nick.split('!')
        justnick = nick[0]
        if justnick == self.client.nick:
            self._msg(config['ownernick'], "RUINBot version 12.3 at your service.")
        


    def parser(self, nick, chan, msg):
        '''Parse commands!'''
        m = self.COMMAND_RE.match(msg)
        if m:
            cmd = m.group(1)
            arg = m.group(2)
            cmd_func = 'cmd_%s' % cmd.upper()
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

        except urllib2.URLError as e:
            logging.info("URLError while retrieving %s" % url, exc_info=True)
        except ValueError as e:
            logging.warning("Unable to examine URL %s" % url, exc_info=True)

    # STANDARD COMMANDS

    def cmd_ABOUT(self, nick, chan, arg):
        if arg == config['ownernick']:
            aboutowner = config.get('aboutowner')
            for item in aboutowner:
                self._msg(chan, "%s" % item)
        else:
            self._msg(chan, "Hi! I'm RUINBot. I am the bot created by Sam van Kampen (with some help from Aiiane/Aeriele/Amber).")
            self._msg(chan, "My code is hosted at GitHub.")

    def cmd_CHOOSE(self, nick, chan, arg):
        """choose - Given a set of items, pick one randomly."""
        usage = lambda: self._msg(chan, "Usage: choose <item> <item> ...")
        items = arg.split()
        if not items:
            return usage()
        else:
                self._msg(chan, "%s: %s" % (nick.split('!')[0], random.choice(items)))

    # ADMIN COMMANDS

    def cmd_JOIN(self, nick, chan, arg):
        nick = nick.split('!')
        nick = nick[0]
        try:
            getAdmin = self.admins[nick].find('true')
        except KeyError:
            getAdmin = -1
        if getAdmin != -1:
            self._msg(chan, "Joining channel %s on request of %s." % (arg, nick))
            helpers.join(self.client, arg)
            logging.info("[JOIN] %s by %s" % (arg, nick))
        else:
            self._msg(chan, "Erm, you aren't an admin...")

    def cmd_PART(self, nick, chan, arg):
        nick = nick.split('!')
        nick = nick[0]
        try:
            getAdmin = self.admins[nick].find('true')
        except KeyError:
            getAdmin = -1
        if getAdmin != -1:
            self._msg(chan, "Parting channel %s on request of %s." % (arg, nick))
            helpers.part(self.client, arg)
            logging.info("[PART] %s by %s" % (arg, nick))
        else:
            self._msg(chan, "Erm, you aren't an admin...")

    def cmd_SETNICK(self, nick, chan, arg):
        try:
            getAdmin = self.admins[nick].find('true')
        except KeyError:
            getAdmin = -1
        if getAdmin != -1:
            usage = lambda: self._msg(chan, "Usage: setnick <nick>")
            if not arg:
                return usage()
            self._msg(chan, "Changing nick to %s!" % arg)
            client.send('NICK', '%s' % arg)
            logging.info("[NICKCHANGE] -> %s" % arg)
        else:
            self._msg(chan, "Erm, you aren't an admin")
            
    def cmd_LOGIN(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: login <password>. Only usable in PM's!")
        nick = nick.split('!')
        nick = nick[0]
        if not arg:
            return usage()
        if self.pm == 1:
            if arg == config['adminpwd']:
                self.admins[nick] = 'true'
                self._msg(nick, "You are now logged in as rank 'admin'.")
        else:
            self._msg(chan, "This command is only usable in a PM.")

    def cmd_DIE(self, nick, chan, arg):
        nick = nick.split('!')
        nick = nick[0]
        try:
            getAdmin = self.admins[nick].find('true')
        except KeyError:
            getAdmin = -1
        if getAdmin != -1:
            self._msg(nick, "Dying.")
            logging.info("Dying. Issued by %s." % (nick))
            sys.exit()

    # SORTA SPECIAL COMMANDS

    def cmd_TWEET(self, nick, chan, arg):
        if config['twitter']['enabled'].upper() != "true":
            self._msg(chan, "tweet is not enabled in this bot, sorry!")
            return
        usage = lambda: self._msg(chan, "Usage: tweet <tweet>")
        
        if not arg:
            return usage()
        
        if arg.lower() == "that":
            arg = self.slm
        
        consumer_key=config['twitter']['consumerkey']
        consumer_secret=config['twitter']['consumersecret']
        
        access_token=config['twitter']['accesstoken']
        access_secret=config['twitter']['accesssecret']
        
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        
        api = tweepy.API(auth)
        username = api.me().name
        logging.info("[TWEEPY] Successfully authenticated via OAuth! Yay! (Uname: '%s')" % username)

        logging.info("[TWEEPY] Updating status...")
        api.update_status('%s' % arg)
        logging.info("[TWEEPY] Updated.")

    # MAINLY FACTOID COMMANDS

    def cmd_REMEMBER(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: remember <trigger> <factoid>")
        if not arg:
            return usage()
        args = arg.split()
        trigger = args[0]
        factoid = args[1]
        existing = db.execute("SELECT id FROM factoids WHERE trigger = ?", (trigger,)).fetchone()
        if existing:
            db.execute("UPDATE factoids SET factoid = ? WHERE trigger = ?", (factoid, existing[0]))
            database.commit()
        else:
            db.execute("INSERT INTO factoids (trigger, factoid) VALUES ('%s', '%s')" % (trigger, factoid))
            database.commit()
        self._msg(chan, "%s now points to %s." % (trigger, factoid))
        logging.info("[INFO] Remembered '%s' (%s)" % (trigger, factoid))

    def cmd_RECALL(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: recall <trigger>")
        nonexistant = lambda: self._msg(chan, "Unable to recall '%s'. Nonexistant?" % arg)
        if not arg:
            return usage()
        args = arg.split()
        trigger = args[0]
        factoid = db.execute("SELECT factoid FROM factoids WHERE trigger = ?", (trigger,)).fetchone()
        if not factoid:
            return nonexistant()
        factoid = factoid[0]
        self._msg(chan, "%s: %s" % (trigger, factoid))
        logging.info("[INFO] Recalled '%s'" % trigger)
        
    def cmd_FORGET(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: forget <trigger>")
        nonexistant = lambda: self._msg(chan, "Unable to forget '%s'. Nonexistant?" % arg)
        if not arg:
            return usage()
        trigger = arg
        factoid = db.execute("SELECT factoid FROM factoids WHERE trigger = ?", (trigger,))
        if not factoid:
            return nonexistant()
        db.execute("DELETE FROM factoids WHERE trigger = ?", (trigger,))
        self._msg(chan, 'Forgot %s!' % trigger)
        database.commit()
        logging.info("Forgot '%s' (%s)" % (trigger, factoid))
        
    # SOME COMIC AND FUN COMMANDS
    
    def cmd_QUOTE(self, nick, chan, arg):
        '''Quote handling!'''
        usage = lambda: self._msg(chan, "Usage: quote [ADD|LIST|GET|RM] [QUOTE|QUOTENUMBER]")
        help = lambda: self._msg(chan, "To split a quote into multiple lines, use the |, for example, 'RaindeerLovers: HAI!|Star: Morning.'")
        if not arg:
            return (usage(), help())
        args = arg.split()
        nick = nick.split('!')
        if args[0].upper() == "ADD":
            quote = ' '.join(args[1:])
            timestamp = strftime("%a, the %dth of %B, %Y")
            db.execute("INSERT INTO quotes (quote, nick, timestamp) VALUES (?, ?, ?)", (quote, nick, timestamp))
            quotenum = db.execute("SELECT id FROM quotes WHERE quote = ?", (quote,))
            self._msg(chan, "Added quote #%s (points to %s) to the quote database" % (quotenum, quote))
            logging.info("Added quote #%s (%s) to the quote database. Added by %s." % (quotenum, quote, nick))
        elif args[0].upper() == "GET":
            quotenum = args[1]
            quote = db.execute("SELECT quote FROM quotes WHERE id = ?", (quotenum,)).fetchone()
            quote = quote.split('|')
            timestamp = db.execute("SELECT timestamp FROM quotes WHERE id = ?" (quotenum,)).fetchone()
            setby = db.execute("SELECT nick FROM quotes WHERE id = ?", (quotenum,)).fetchone()
            self._msg(chan, "Quote number %s:" % (quotenum))
            for i in quote:
                print(i)
            self._msg(chan, "Added by %s on %s" % (nick, timestamp))
        elif args[0].upper() == "RM":
            quotenum = args[1]
            nonexistant = lambda: self._msg(chan, "Unable to forget quote #%s. Nonexistant?" % quotenum)
            quote = db.execute("SELECT quote FROM quotes WHERE id = ?", (quotenum,)).fetchone()
            if not quote:
                return nonexistant()
            db.execute("DELETE FROM factoids WHERE id = ?", (quotenum,))
            self._msg(chan, "Forgot #%s (pointed to %s)!" % (quotenum, quote))
            logging.info("Forgot quote #%s (%s). Forgot by %s." % (quotenum, quote, nick))
        else:
            self._msg(chan, "Unknown quote operation %s." % args[0])

    def cmd_CMDS(self, nick, chan, arg):
        self._msg(chan, "Commands: join*, part*, setnick*, login**, about, quote, choose, tweet, remember, recall, forget")
        self._msg(chan, "* = Owner Only ** = PM only.")

    # SPECIAL MODE COMMANDS
            
    def cmd_OPERUP(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: operup (duh)")
        opernick = config['oper']['nick']
        operpass = config['oper']['pass']
        client.send('OPER', opernick, operpass)
        logging.info("[INFO] Opered up!")
        self.operedup = True

    def _msg(self, chan, msg):
        helpers.msg(self.client, chan, msg)

if __name__ == '__main__':
    
        with open('config.yaml') as f:
            config = yaml.safe_load(f)
    
        database = sqlite3.connect(config['db']['path'])
        db = database.cursor()
        db.execute("""CREATE TABLE IF NOT EXISTS factoids (id INTEGER PRIMARY KEY AUTOINCREMENT, trigger TEXT, factoid TEXT)""")
        db.execute("""CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT, nick TEXT, timestamp TEXT)""")
        database.commit()
    
    

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

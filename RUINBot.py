#!/usr/bin/env python
#
# RUINBot version 23022012
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

import json, urllib2, functools, tweepy, urllib
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
                if nick == 'svkampen!svkampen@Srs.Face' or nick == 'neoinr!robin@flp.st':
                        return f(self, nick, chan, arg)
                elif nick == 'Nagah!max@Acael.us':
                    return self._msg(chan, "NO ADMEEN FOR YU!")
                else:
                        return self._msg(chan, "Permission Denied.")
        return wrapper
    
class RUINHandler(DefaultCommandHandler):

    def __init__(self, *args, **kwargs):
        super(RUINHandler, self).__init__(*args, **kwargs)
        self.COMMAND_RE = re.compile(r"^(?:%s:\s+|%s)(\w+)(?:\s+(.*))?$" % (self.client.nick, re.escape(config['cmdchar'])))
        self.operedup = None
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

    def join(self, nick, chan):
        nick = nick.split('!')
        justnick = nick[0]
        if justnick == "RUINBot":
            return
        self.seennick(justnick, chan)
        self.setnickmodes(justnick, chan)
        self.news("JOINNEWS", chan)
        
    
    def news(self, newstype, chan):
        news = db.execute("SELECT news FROM news WHERE newstype = ? AND chan = ?", (newstype, chan))
        rawnews = news[0]
        self._msg(chan, "Join News for %s: %s" % (chan, rawnews))

    def seennick(self, nick, chan):
        seen = db.execute("SELECT seen FROM nickrecall WHERE nick = ?", (nick,)).fetchone()
        if not seen:
            self._msg(chan, "Welcome to %s, %s! Join #minecraft for server chat." % (chan, nick))
            db.execute("INSERT INTO nickrecall (seen, chan) VALUES ('TRUE', '%s')" % chan)
            return
        self._msg(chan, "Welcome back, %s!" % nick)
                
    def setnickmodes(self, nick, chan):
        modes = db.execute("SELECT modes FROM nickrecall WHERE nick = ? AND chan = ?", (nick, chan)).fetchone()
        if not modes:
            return
        client.send('MODE', '%s', modes, '%s' % (chan, nick))
        
    def parser(self, nick, chan, msg):

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

    @admin_only
    def cmd_SETNICK(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: setnick <nick>")
        if not arg:
            return usage()
        self._msg(chan, "Changing nick to %s!" % arg)
        client.send('NICK', '%s' % arg)
        logging.info("[NICKCHANGE] -> %s" % arg)

    # SORTA SPECIAL COMMANDS

    def cmd_TWEET(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: tweet <tweet>")
        
        if not arg:
            return usage()
        
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
        
    def cmd_PASTEBIN(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "pastebin <stuffstuff>")
        
        if not arg:
            return usage()
        
        url = 'http://pastebin.com/api/api_post.php'
        
        values = {'api_dev_key' : '120c7c03f4960b390931ee922605c0f0',
                  'api_paste_code' : '%s',
                  'api_option' : 'paste' % arg,
                  }

        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            
            pasteurl = response.read()
            print("Paste URL: %s" % pasteurl)
        except Exception, detail:
            print "Error: ", detail

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
        result = db.execute("DELETE FROM factoids WHERE trigger = ?", (trigger,))
        if not result:
            return nonexistant()
        self._msg(chan, 'Forgot %s!' % trigger)
        logging.info("Forgot '%s' (%s)" % (trigger, factoid))
        
    # SOME COMIC AND FUN COMMANDS
    
    def cmd_XKCD(self, nick, chan, arg):
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
        

    def cmd_SPACE(self, nick, chan, arg):
        self._msg(chan, "%s%s%s" % ("Sp","a"*int(arg),"ce"))
        logging.info("[CMDS] Executed.")

    def cmd_CMDS(self, nick, chan, arg):
        self._msg(chan, "Commands: [@join]*, [@part]*, [@xkcd], [@about], [@teehee], [@ruinsite], [@space], [@choose], [@tweet], [@remember], [@recall]")
        self._msg(chan, "* = Owner Only")

    # SPECIAL MODE COMMANDS
    
    @admin_only
    def cmd_SETAUTOMODES(self, nick, chan, arg):
        usage = lambda: self._msg(chan, "Usage: setautomodes <nick> <modes> <chan>")
        notopered = lambda: self._msg(chan, "[ERR]Not opered up!")
        if not arg:
            return usage()
        if not self.operedup:
            return notopered()
        
        args = arg.split()
        nick = args[0]
        modes = args[1]
        chan = args[2]
        
        existing = db.execute("SELECT modes FROM nickrecall WHERE nick = ? AND chan = ?", (nick, chan)).fetchone()
        if existing:
            db.execute("UPDATE nickrecall SET modes = ? WHERE nick = ? AND chan = ?", (modes, nick, chan))
            database.commit()
        else:
            db.execute("INSERT INTO nickrecall (modes, nick, chan) VALUES (?,?,?)", (modes, nick, chan))
            database.commit()
            
        logging.info("[INFO] Auto modes set for nick %s: %s in chan %s" % (nick, modes, chan))
            
    @admin_only
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
        db.execute("""CREATE TABLE IF NOT EXISTS nickrecall (nick TEXT, chan TEXT, modes TEXT, seen TEXT)""")
        db.execute("""CREATE TABLE IF NOT EXISTS factoids (id INTEGER PRIMARY KEY AUTOINCREMENT, trigger TEXT, factoid TEXT)""")
        db.execute("""CREATE TABLE IF NOT EXISTS news (news TEXT, newstype TEXT, setby TEXT, chan TEXT)""")
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

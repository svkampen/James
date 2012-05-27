#!/usr/bin/env python
#
# James version 12.4
# Build Date: 21042012
# 
# (C) 2012 Sam van Kampen
#
# Some of the main code copied from Kitn (as there is no Oyoyo documentation)
# That code (C) 2011 Amber Yust =)
# 
# https://github.com/svkampen/James/wiki/About
# 

from oyoyo.client import IRCClient, IRCApp
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import json, urllib2, tweepy, urllib, time, logging, yaml, re, sys, sqlite3, traceback, random
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup as soup

logging.basicConfig(level=logging.INFO)
config = None
app = None
    
class JamesHandler(DefaultCommandHandler):

    def __init__(self, *args, **kwargs):
        """Handles initial actions."""
        super(JamesHandler, self).__init__(*args, **kwargs)
        self.COMMAND_RE = re.compile(r"^(?:%s:\s+|%s)(\w+)(?:\s+(.*))?$" % (self.client.nick, re.escape(config['cmdchar'])))
        self.operedup = None
        self.messages = dict()
        self.messages['lm'] = ""
        self.admins = []
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
		""" Message receival """
        logging.info("Message received: [%s] <%s>: %s " % (chan, nick, msg))
        botnick = self.client.nick
        botnick = botnick.upper()
        nick = nick.split('!')[0]
        
        if chan.upper() == botnick and nick != botnick:
            self.pm = 1
            if not msg.startswith(config['cmdchar']):
                self._msg(nick, "Unknown command..")
        else:
            self.pm = 0


        self.messages['slm'] = self.messages['lm']
        self.messages['lm'] = msg     
        self.parser(nick, chan, msg)

    def join(self, nick, chan):
        nick = nick.split('!')[0]
        if nick != self.client.nick:
            self._msg(chan, "Welcome to %s, %s!" % (chan, nick))
            self.checkMail(nick)

    def parser(self, nick, chan, msg):
        """Parse commands!"""
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
        self._msg(chan, "Hi! I'm James. I am the bot created by Sam van Kampen (with some help from Aiiane/Aaeriele/Amber).")
        self._msg(chan, "My code is hosted at GitHub. http://git.tehsvk.net/James/")

    def cmd_CHOOSE(self, nick, chan, arg):
        """choose - Given a set of items, pick one randomly."""
        usage = lambda: self._msg(chan, "Usage: choose <item> <item> ...")
        items = arg.split()
        if not items:
            return usage()
        else:
                self._msg(chan, "%s: %s" % (nick.split('!')[0], random.choice(items)))

    def _cmd_MEME(self, nick, chan, arg):
        """meme - search for a meme on KnowYourMeme"""
        usage = lambda: self._msg(chan, "Usage: meme <query>")
        if not arg:
            return usage()

        self._msg(chan, "http://knowyourmeme.com/search?%s" % urlencode({'q': arg}))
        

    # MAIL COMMANDS
    def cmd_MAIL(self, nick, chan, arg):
	    """ Get, read, send and delete serverwide mail."""
		args = arg.split()
		nick = nick.split('!')
		if not arg:
			usage = lambda: self._msg(chan, "Usage: mail <send|get|read|delete> [user] [message] [ID]")
			example = lambda: self._msg(chan, "Example: mail send neoinr I like cows")
		    return (usage(), example())

        if args[0] == "send":
			# Sending mail.
			timestamp = time.strftime("[%H:%M]")
			user = args[1]
			message = ' '.join(args[2:])
			self._msg(chan, "Sending message '%s' to user %s..." % (message, user)
			db.execute("INSERT INTO mail (message, user, sentby, timestamp) VALUES (?,?,?)", (message, user, nick, timestamp))
			database.commit()
			self._msg(chan, "Done.")
			
		elif args[0] == "get":
			ids = db.execute("SELECT id FROM mail WHERE user = ?", (nick,)).fetchall()
			timestamps = db.execute("SELECT timestamp FROM mail WHERE user = ?", (nick,)).fetchall()
			messages = db.execute("SELECT message FROM mail WHERE user = ?", (nick,)).fetchall()
			sent-bys = db.execute("SELECT sentby FROM mail WHERE user = ?", (nick,)).fetchall()
			num = 0
			
			if len(timestamps) != 0:
			    while num < (len(timestamps)-1):
				    self._msg(chan, "[%s] %s  %s...        %s" % (ids[num], timestamps[num], messages[num][:-(len(messages[num]/3)], sent-bys[num]))
    				num = num + 1
			
	    		self._msg(chan, "\nTotal of %d messages." % ((len(messages)-1))
	    	
	    	else:
				self._msg(chan, "No messages found.")
				
			
		elif args[0] == "read":
			msgid = args[1]
			message = db.execute("SELECT message FROM mail WHERE id = ?", (msgid,)).fetchone()
			sentby = db.execute("SELECT sentby FROM mail WHERE id = ?", (msgid,)).fetchone()
			
			self._msg(chan, "Message-id: %d" % (msgid))
			self._msg(chan, "\n")
			self._msg(chan, "%s")
			self._msg(chan, "\nSent by: %s, at %s" % (sentby, timestamp))
			
		elif args[0] == "delete" or args[0] == "rm":
			msgid = args[1]
			message = db.execute("SELECT message FROM mail WHERE id = ?", (msgid,)).fetchone()
			db.execute("DELETE FROM mail WHERE id = ?", (msgid,))
			self._msg(chan, "Deleted message '%s' (message id: %s')" % (message, msgid))
			database.commit()
			
			
			
			
			

    # ADMIN COMMANDS

    def cmd_EVAL(self, nick, chan, arg):
		""" Evaluate an expression. """
        nick = nick.split('!')[0]
        args = arg.split()
        if nick in self.admins:
            admin = True
        else:
            admin = False
        if admin:
            # Yay for better syntax up in hear.
            self._msg(chan, 'Evaluating Python code...')
            if not '-r' in args:
                eval(' '.join(args[0:]))
            elif '-r' in args:
                print(eval(' '.join(args[1:])))
            else:
                self._msg(chan, 'Unknown amount of arguments; aborting.')
                return
            self._msg(chan, 'Done.')

        else:
            self._msg(chan, "Erm, you aren't an admin...")

    def cmd_JOIN(self, nick, chan, arg):
        nick = nick.split('!')[0]
        
        if nick in self.admins:
            admin = True
        else:
            admin = False
        if admin == True:
                self._msg(chan, "Joining channel %s on request of %s." % (arg, nick))
                helpers.join(self.client, arg)
                logging.info("[JOIN] %s by %s" % (arg, nick))
        else:
            self._msg(chan, "Erm, you aren't an admin...")
            
    def cmd_PART(self, nick, chan, arg):
        nick = nick.split('!')[0]
        
        if nick in self.admins:
            admin = True
        else:
            admin = False
        if admin == True:
            self._msg(chan, "Parting channel %s on request of %s." % (arg, nick))
            helpers.part(self.client, arg)
            logging.info("[PART] %s by %s" % (arg, nick))
        else:
            self._msg(chan, "Erm, you aren't an admin...")

    def cmd_SETNICK(self, nick, chan, arg):
        nick = nick.split('!')[0]
        
        if nick in self.admins:
            admin = True
        else:
            admin = False
        if admin == True:
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
        nick = nick.split('!')[0]
        
        if not arg:
            return usage()
        if self.pm == 1:
            if nick in self.admins:
                self._msg(nick, "You are already logged in!")
            if arg == config['adminpwd']:
                self.admins.append(nick)
                self._msg(nick, "You are now logged in.")
            else:
                self._msg(nick, "Incorrect password.")
        else:
            self._msg(chan, "This command is only usable in a PM.")
    
    def cmd_LOGOUT(self, nick, chan, arg):
        nick = nick.split('!')[0]
        
        if self.pm == 1:
            self.admins.remove(nick)
            self._msg(nick, "You have been logged out. Have a nice day!")
        else:
            self._msg(chan, "This command is only usable in a PM.")

    # SORTA SPECIAL COMMANDS

    def cmd_TWEET(self, nick, chan, arg):
        if config['twitter']['enabled'].upper() != "TRUE":
            self._msg(chan, "tweet is not enabled in this bot, sorry!")
            return
        usage = lambda: self._msg(chan, "Usage: tweet <tweet>")
        
        if not arg:
            return usage()
        

        
        if arg.lower() == "that":
            arg = self.messages['slm']
        
        consumer_key=config['twitter']['consumerkey']
        consumer_secret=config['twitter']['consumersecret']
        
        access_token=config['twitter']['accesstoken']
        access_secret=config['twitter']['accesssecret']
        
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        
        api = tweepy.API(auth)
        username = api.me().name
        logging.info("[TWEEPY] Successfully authenticated via OAuth! Yay! (Uname: '%s')" % username)
        
        if arg.lower() == "getlatesttweet":
            pub = api.home_timeline()
            self._msg(chan, "Latest tweet is: '%s'" % pub[0].text)
            return
         
        
        logging.info("[TWEEPY] Updating status...")
        api.update_status('%s' % arg)
        logging.info("[TWEEPY] Updated.")
        
        last_updated_by = nick
        
        self._msg(chan, "Updated twitter status to '%s' (executed by '%s')" % (arg, nick))

    # MAINLY FACTOID COMMANDS

    def cmd_REMEMBER(self, nick, chan, arg):
		""" Remember a factoid """
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
		""" Recall a factoid """
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
		""" Forget a factoid """
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
        
        
        
    def cmd_CMDS(self, nick, chan, arg):
		""" Gimme those commands! """
		if not arg:
			usage = lambda: self._msg(chan, "Usage: cmds <cmdtype>")
	        types = lambda: self._msg(chan, "Types: owner, normal, pm")
            
            return (usage(), types())
        
        if arg == "owner":
			self._msg(chan, "==  Owner Commands ==")
			self._msg(chan, "==      join       ==")
			self._msg(chan, "==      part       ==")
			self._msg(chan, "==      setnick    ==")
			self._msg(chan, "==      eval       ==")
			self._msg(chan, "=====================")
			
		elif arg == "normal":
			self._msg(chan, "== Normal Commands ==")
			self._msg(chan, "==     about       ==")
			self._msg(chan, "==     quote       ==")
			self._msg(chan, "==     choose      ==")
			self._msg(chan, "==     tweet       ==")
			self._msg(chan, "==     remember    ==")
			self._msg(chan, "==     recall      ==")
			self._msg(chan, "==     forget      ==")
			self._msg(chan, "==     mail        ==")
			self._msg(chan, "=====================")
		
		elif arg == "pm":
			self._msg(chan, "==   PM Commands   ==")
			self._msg(chan, "==     login       ==")
			self._msg(chan, "==     logout      ==")
			self._msg(chan, "=====================")
			
        else:
			self._msg(chan, "Unknown command type: %s" % (arg))
			return

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
        db.execute("""CREATE TABLE IF NOT EXISTS mail (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, user TEXT, sentby TEXT, timestamp TEXT)""")
        database.commit()
    
    

        app = IRCApp()
        clients = {}
        for server, conf in config['servers'].iteritems():
           client = IRCClient(
           JamesHandler,
           host=server,
           port=conf['port'],
           nick=conf['nick'],
           real_name=conf['name'],
        )
        clients[server] = client
        app.addClient(client)
        app.run()

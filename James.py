#!/usr/bin/env python
#
# Build Date: 12012013
# 
# (C) 2012-2013 Sam van Kampen
#
# Some of the main code copied from Kitn (as there is no Oyoyo documentation)
# That code (C) 2011 Amber Yust =)
#
# Also some of the code is from rmmh/skybot. Again, that code (C) rmmh et al.
# 
# https://github.com/svkampen/James/wiki/About
# 

from oyoyo.client import IRCClient, IRCApp
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
import json, urllib2, tweepy, logging, yaml, re, sys, sqlite3, random, os
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup as soup

from threading import Thread
from lxml import etree # OMG XML
from urllib import urlencode

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
        self.admins = ['svkampen', 'neoinr']
        self.nicklist = []
        self.definedcommands = []


    class UrbanSearch(Thread):

        def _get_json(self, url):
            url = url.replace(' ', '%20')
            page = urllib2.urlopen(url)
            data = json.loads(page.read())
            return data

        def run(self, james, chan, nick, num, showlink, url):
            data = self._get_json(url)

            defs = data['list']

            if data['result_type'] == 'no_results':
                return 'not found.'

            out = defs[num]['word'] + ': ' + defs[num]['definition']

            readmore = False

            if len(out) > 200:
                out = out[:out.rfind(' ', 0, 200)] + '...'
                readmore = True
            
            out = out.strip('\n')

            james._msg(chan, "%s: %s" % (nick.split('!')[0],out))
            if readmore or showlink:
                #james._msg(chan, "  ")
                james._msg(chan, "Read more: %s" % james._shorten(defs[num]['permalink']))




    def welcome(self, nick, chan, msg):
        # I had a lot of trouble doing this, so most of the code is copied from Amber (as this seems a great way)
        """Trigger on-login actions via the WELCOME event."""
        s = config['servers'][self.client.host]
        # If an auth is specified, use it.
        auth = s.get('auth')
        if auth['to']:
            try:
                self._msg(auth['to'], auth['msg'])
            except KeyError:
                logging.error('Authentication info for %s missing "to" or "msg", skipping.' % self.client.host)
        # If default channels to join are specified, join them.
        channels = s.get('channels', ())
        for channel in channels:
            helpers.join(self.client, channel)        
        # If server-specific user modes are specified, set them.
        modes = s.get('modes')
        if modes:
            self.client.send('MODE', s["nick"], modes)
        logging.info("Completed connection actions for %s." % self.client.host)



    def privmsg(self, nick, chan, msg):
        """ Message receival """
        realnick = nick.split('!')[0]
        logging.info("Message received: [%s] <%s>: %s " % (chan, nick, msg))
        if not realnick in self.nicklist:
            self.nicklist.append(realnick)
            logging.info("Added nick to nicklist: %s" % realnick)

        botnick = self.client.nick
        botnick = botnick.upper()
        nick = nick.split('!')[0]
        
        if chan.upper() == botnick and nick.upper() != botnick:
            self.pm = 1
            if not msg.startswith(config['cmdchar']):
                self._msg(nick, "Unknown command..")
        else:
            self.pm = 0

        self.messages['slm'] = self.messages['lm']
        if 'http://' in msg:
            self.messages['htm'] = msg
        self.messages['lm'] = msg     
        self.messages[nick.split('!')[0]] = msg
        self.parser(nick, chan, msg)

    # <UnoAphex> Make it so it just shuts the fuck up
    # <UnoAphex> until asked
    #
    # Edit: <neoinr> Make him call Acaelus a snailus
    def join(self, nick, chan):
        nick = nick.split('!')[0]
        if nick.lower() in ("acaelus", "nagah", "nagger", "fishermanfrommontreal"):
            self._msg(chan, "Acaelus, snailus, as big as a whaleus.")

    def parser(self, nick, chan, msg):
        """Parse commands!"""
        if 'twitter.com' in msg and 'status' in msg:
            self._get_status(chan, msg)
            return

        m = self.COMMAND_RE.match(msg)
        if m:
            cmd = m.group(1).upper()
            arg = m.group(2)
            cmd_func = 'cmd_%s' % cmd
            if hasattr(self, cmd_func):
                try:
                    getattr(self, cmd_func)(nick, chan, arg)
                except:
                    logging.error("Exception while attempting to process command '%s'" % cmd, exc_info=True)
                # Don't try to parse a URL in a recognized command
                return


    def _get_xml(self, url):
        return etree.fromstring(urllib2.urlopen(url).read())

    def _get_json(self, url):
        url = url.replace(' ', '%20')
        page = urllib2.urlopen(url)
        data = json.loads(page.read())
        return data


    # STANDARD COMMANDS

    def cmd_WIKI(self, nick, chan, arg):
        return self._msg(chan, 'http://en.wikipedia.org/wiki/%s'.replace('=', '') % (urlencode({'': arg})))

    def cmd_REGISTER(self, nick, chan, arg):
        self._msg('NickServ', 'logout')
        self._msg('NickServ', 'register kikkerfish sam@tehsvk.net')
        logging.info('Registered with NickServ')

    def cmd_DEF(self, nick, chan, arg):
        self.definedcommands.append(arg[:arg.find('(')])
        exec 'global '+arg[:arg.find('(')].rstrip()+'\ndef '+(arg.replace('\\n', '\n')).replace('\\t', '    ')
        self._msg(chan, "Added function.")

    def cmd_ABOUT(self, nick, chan, arg):
        self._msg(chan, "Hi! I'm James. I am an IRC bot! Use +help to see my commands.")
        self._msg(chan, "My code is hosted at GitHub. http://git.tehsvk.net/James/")

    def cmd_CHOOSE(self, nick, chan, arg):
        """choose - Given a set of items, pick one randomly."""
        usage = lambda: self._msg(chan, "Usage: choose <item> <item> ...")
        items = arg.split()
        if not items:
            return usage()
        else:
                self._msg(chan, "%s: %s" % (nick.split('!')[0], random.choice(items)))

    def cmd_MEME(self, nick, chan, arg):
        """meme - search for a meme on KnowYourMeme"""
        usage = lambda: self._msg(chan, "Usage: meme <query>")
        if not arg:
            return usage()

        self._msg(chan, "http://knowyourmeme.com/search?%s" % urlencode({'q': arg}))
        
    def cmd_WEATHER(self, nick, chan, arg):
        """ OMG WEATHER FROM GOOGLE USING XML """
        if not arg:
            return self._msg(chan, "Usage: +weather <city>")
        weather = self._get_xml("http://google.com/ig/api?%s" % (urlencode({'weather': arg})))
        weather = weather.find('weather')
        
        winfo = dict((item.tag, item.get('data')) for item in weather.find('current_conditions'))
        winfo['city'] = weather.find('forecast_information/city').get('data')
        winfo['high'] = weather.find('forecast_conditions/high').get('data')
        winfo['low'] = weather.find('forecast_conditions/low').get('data')
        self._msg(chan, "Weather for %(city)s: %(condition)s - %(temp_f)sF/%(temp_c)sC - %(humidity)s" % winfo)

    # MAIL COMMANDS
    def cmd_MD5(self, nick, chan, arg):
        ''' MD5 hashing. I know md5's module is deprecated. Fuck you. '''
        from md5 import md5
        self._msg(chan, "%s: %s" % (nick.split('!')[0], md5(arg).hexdigest()))            

    def cmd_QUIT(self, nick, chan, arg):
        os.abort()

    def cmd_NYT(self, nick, chan, arg):
        ''' Search using the NYT Article API '''
        if not arg:
            self._msg(chan, "Usage: nyt [type] [query]")
            self._msg(chan, "More information: http://bit.ly/KC5NGV")

        args = arg.split()
    
        type = args[0]
        query = ' '.join(args[1:]).replace(" ", "%20")
        url = 'http://api.nytimes.com/svc/search/v1/article?%s&api-key=%s' % (urlencode({'query': query}), '0b5514a882c37ad59137c1c6cc4fad24:9:66203467')

        data = self._get_json(url)

        if type == "read":
            shorturl = self._shorten(data['results'][0]['url']) # Shorten with bitly!
            if not ';' in data['results'][0]['title']:
                self._msg(chan, data['results'][0]['title']+ ' -- ' + data['results'][0]['date'] + ' -- ' + shorturl)
            else:
                self._msg(chan, data['results'][0]['title'].split(';')[1] + ' -- ' + data['results'][0]['date'] + ' -- ' + shorturl)
            self._msg(chan, "\n%s" % (data['results'][0]['body'].replace('&rdquo', "'").replace("&ldquo;", "'").replace("&rsquo;", "'")+"..."))
            self._msg(chan, "Read more: %s" % shorturl)

        elif type == "search":
            num = 1
            while num <5:
                shorturl = self._shorten(data['results'][num]['url']) # Same as above!
                if not ';' in data['results'][num]['title']:
                    self._msg(chan, "\x02%s.\x02 -- %s - %s" % (str(num), data['results'][num]['title'], shorturl))
                else:
                    self._msg(chan, "\x02%s.\x02 -- %s - %s" % (str(num), data['results'][num]['title'].split(';')[1], shorturl))            

                num = num + 1

    def cmd_LMGTFY(self, nick, chan, arg):
        self._msg(chan, "http://lmgtfy.com/?q=%s" % arg.replace(' ', '%20'))

    def cmd_BITLY(self, nick, chan, arg):
       ''' Bit.ly shortener '''
       if 'that' == arg:
           arg = self.messages['htm']
       if ': ' in arg:
           arg = ' '.join(arg.split(': ')[1:])

       out = self._shorten(arg)
       self._msg(chan, "%s: %s" % (nick.split('!')[0], out))

    def cmd_NIGGR(self, nick, chan, arg):
        ''' nig.gr shortener. '''
        out = urllib2.urlopen('http://nig.gr/api/%s' % arg.replace(' ','%20')).read()
        self._msg(chan, '%s: %s' % (nick.split('!')[0], out))

    def _shorten(self, arg):
       if not arg:
           return self._msg(chan, "Usage: bitly <url>")
      
       if not arg.startswith('http'):
           arg = 'http://' + arg

       url = 'http://api.bit.ly/shorten?version=2.0.1&%s&login=svkampen&apiKey=R_a48d3cdf1246bfc2005db3fd35be3d95&format=json' % (urlencode({'longUrl': arg}))
       data = self._get_json(url)

       return data['results'][arg]['shortUrl']

    def cmd_BING(self, nick, chan, arg):
        ''' BING? FUCK BING! '''
        self._msg(chan, "Bing? FUCK BING!")
            
    def cmd_MTGOX(self, nick, chan, arg):
        url = 'https://mtgox.com/code/data/ticker.php'
        data = self._get_json(url)

        ticker = data['ticker']
        self._msg(chan, "Current: %s - Volume: %s" % (ticker['buy'], ticker['vol']))

    def cmd_GOOGLE(self, nick, chan, arg):
        ''' Googling! '''
        if not arg:
            return self._msg(chan, "Usage: google [query]")

        args = arg.split()
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&%s' % (urlencode({'q': ' '.join(args[0:])}))

        data = self._get_json(url)

        if len(data['responseData']['results']) == 0:
            self._msg(chan, "%s: No results found." % nick.split('!')[0])
            return

        results = data['responseData']['results']

        self._msg(chan, "\x02%s\x02 -- %s" % (results[0]['url'], results[0]['titleNoFormatting']))

    def cmd_URBAN(self, nick, chan, arg):
        ''' UrbanDictionary lookup. '''

        if not arg:
            return self._msg(chan, "Usage: urban [phrase]")

        args = arg.split()

        showlink = False

        if '-n' in args:
            if '--showlink' in args:
                args.remove('--showlink')
                showlink = True
            num = int(args[1]) - 1
            url = 'http://www.urbandictionary.com/iphone/search/define?%s' % (urlencode({'term': ' '.join(args[2:])}))
        else:
            if '--showlink' in args:
                args.remove('--showlink')
                showlink = True
            num = 0
            url = 'http://www.urbandictionary.com/iphone/search/define?%s' % (urlencode({'term': ' '.join(args[0:])}))
        
        urbanSearch = self.UrbanSearch()
        urbanSearch.run(self,chan, nick,num,showlink,url)

    def cmd_ADDFILTER(self, nick, chan, arg):
        self.filters.append(arg.lower())

    def cmd_DELFILTER(self, nick, chan, arg):
        self.filters.append(arg.lower())

    # ADMIN COMMANDS

    def cmd_EVAL(self, nick, chan, arg):
        """ Evaluate an expression. """
        if self.pm:
            chan = nick.split('!')[0]
        nick = nick.split('!')[0]
        args = arg.split()
        if nick in self.admins:
            admin = True
        else:
            admin = False
        if admin:
            # Yay for better syntax up in hear.
            if not '-r' in args:
                eval(' '.join(args[0:]))
            elif '-r' in args:
                print(eval(' '.join(args[1:])))
            else:
                self._msg(chan, 'Unknown amount of arguments; aborting.')
                return

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
        if self.pm == 1 or self.pm == 0:
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

    def cmd_TWITTER(self, nick, chan, arg):
        return self._msg(chan, "http://twitter.com/#!/JamesIRCBot")

    def cmd_TWEET(self, nick, chan, arg):
        if nick.split('!')[0] not in self.admins or 'neoinr' in nick.split('!')[0]:
            self._msg(chan, "Erm.. you are not an admin.")
            return

        if config['twitter']['enabled'].upper() != "TRUE":
            self._msg(chan, "tweet is not enabled in this bot, sorry!")
            return
        usage = lambda: self._msg(chan, "Usage: tweet <tweet>")
        
        if not arg:
            return usage()
        

        
        if arg.lower() == "that":
            arg = self.messages['slm']

        if arg in self.nicklist:
            arg = self.messages[arg]
        
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
        api.update_status('%s' % (arg))
        logging.info("[TWEEPY] Updated.")
        
        last_updated_by = nick
        
        self._msg(chan, "Updated twitter status to '%s' (executed by %s)" % (arg, nick))

    # MAINLY FACTOID COMMANDS

    def cmd_REMEMBER(self, nick, chan, arg):
        """ Remember a factoid """
        usage = lambda: self._msg(chan, "Usage: remember <trigger> <factoid>")
        if not arg:
            return usage()
        args = arg.split()
        if len(' '.join(arg.split('/')[:1]).split()) < 2:
            trigger = nick.split('!')[0]
            factoid = ' '.join(args)
        else:
            trigger = args[0]
            factoid = ' '.join(args[1:])


        existing = db.execute("SELECT id FROM factoids WHERE trigger = ?", (trigger,)).fetchone()
        if existing:
            db.execute("UPDATE factoids SET factoid = ? WHERE trigger = ?", (factoid, existing[0]))
            database.commit()
        else:
            db.execute("INSERT INTO factoids (trigger, factoid) VALUES (?, ?)", (trigger, factoid))
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
            ''' self._msg(chan, "==  Owner Commands ==")
            self._msg(chan, "==      join       ==")
            self._msg(chan, "==      part       ==")
            self._msg(chan, "==      setnick    ==")
            self._msg(chan, "==      eval       ==")
            self._msg(chan, "=====================") '''

            self._msg(nick.split('!')[0], "Owner Commands: join, part, setnick, eval, tweet")
            
        elif arg == "normal":
            ''' self._msg(chan, "== Normal Commands ==")
            self._msg(chan, "==     about       ==")
            self._msg(chan, "==     bitly       ==")
            self._msg(chan, "==     google (g)  ==")
            self._msg(chan, "==     quote       ==")
            self._msg(chan, "==     choose      ==")
            self._msg(chan, "==     tweet       ==")
            self._msg(chan, "==     remember    ==")
            self._msg(chan, "==     recall      ==")
            self._msg(chan, "==     forget      ==")
            self._msg(chan, "==     mail        ==")
            self._msg(chan, "==     mtgox       ==")
            self._msg(chan, "==     urban (u)   ==")
            self._msg(chan, "=====================") '''

            self._msg(nick.split('!')[0], "Normal Commands: about, bitly, niggr, google (g), urban (u), choose, tweet, remember, recall, forget, nyt, fuck, approvefuck, setruse, spamruse, mail, mtgox")
        
        elif arg == "pm":
            ''' self._msg(chan, "==   PM Commands   ==")
            self._msg(chan, "==     login       ==")
            self._msg(chan, "==     logout      ==")
            self._msg(chan, "=====================") '''
            
            self._msg(nick.split('!')[0], "PM Commands: login, logout")
            
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

    def cmd_REQUEST(self, nick, chan, arg):
        self.newfeats.append(arg.lower())

    def cmd_GETREQS(self, nick, chan, arg):
        self._msg(chan, "%s" % self.newfeats)

    def _msg(self, chan, msg):
        helpers.msg(self.client, chan, msg)

    def cmd_STONE(self, nick, chan, arg):
        self.client.send("KILL %s :NOU!" % (arg))
        self.killlist.append(arg)
        self._msg(chan, "Successfully stoned! (lol?)")

    def cmd_U(self, nick, chan, arg):
        self.cmd_URBAN(nick, chan, arg)

    def cmd_G(self, nick, chan, arg):
        self.cmd_GOOGLE(nick, chan, arg)

    def cmd_HELP(self, nick, chan, arg):
        self.cmd_CMDS(nick, chan, 'normal')

if __name__ == '__main__':
    
        try:
            config = sys.argv[1]
        except:
            config = 'config.yaml'

        with open(config) as f:
            config = yaml.safe_load(f)
    
        database = sqlite3.connect(config['db']['path'])
        db = database.cursor()

        db.execute("""CREATE TABLE IF NOT EXISTS factoids (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                           trigger TEXT,
                                                           factoid TEXT
                                                           )""")

        db.execute("""CREATE TABLE IF NOT EXISTS mail (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                       message TEXT,
                                                       user TEXT,
                                                       sentby TEXT,
                                                       timestamp TEXT
                                                       )""")
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


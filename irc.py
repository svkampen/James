""" 
IRC - irc.py
"""

from straight.plugin import load
import utils
import sys
import traceback

config = {}
is_debugging = False

class IRC():
    """ IRC(Dict<string, object> config) - the bot class """
    def __init__(self, bconfig):
        globals()["config"] = bconfig
        server = config["server"]
        self.sock = utils.secs.get_socket((server[:-5], int(server[-4:])))
        plugins = load(config["plugdir"])
        self.cmdhandler = utils.commandhandler.CommandHandler(plugins)
        self.running = True
        self.jchans = config["joinchans"]
        self.buff = utils.buffer.Buffer()
        self.has_been_welcomed = False
        self.admins = []
        self.mainloop()

    def mainloop(self):
        """ The IRC Main Loop - run while self.running """
        loops = 0
        try:
            while self.running and self.buff.append(utils.secs.get_data(self.sock)):
                if loops == 0:
                    self.sendnick()
                    self.senduser()
                for msg in self.buff:
                    pmsg = utils.parse.parse(msg)
                    if pmsg["method"] == 'PING':
                        self._send("PONG "+pmsg["arg"])
                    elif pmsg["method"] == utils.num.num["endofmotd"]:
                        self.has_been_welcomed = True
                        print("[INFO]: 376 has passed")
                    elif self.has_been_welcomed:
                        self.joinchans()
                        self.has_been_welcomed = False 
                        # not technically true but whatever
                    else:
                        if hasattr(self, pmsg['method'].lower()):
                            getattr(self, pmsg['method'].lower())(pmsg)
                 
                    loops = +1
                
        except KeyboardInterrupt:
            sys.exit()

    def privmsg(self, msg):
        """ Handles messages """
        nick = msg["host"].split('!')[0]
        chan = msg["arg"].split()[0]
        msg = msg["arg"].split(' ', 1)[1][1:]
        print("[%s] <%s> %s" % (chan, nick, msg))
        if msg.startswith(config["cmdchar"]):
            try:
                cmd_splitmsg = msg.split(" ", 1)
                cmd_name = cmd_splitmsg[0][1:]
                if len(cmd_splitmsg) > 1:
                    cmd_args = cmd_splitmsg[1]
                else:
                    cmd_args = ''
                callback = self.cmdhandler.trigger(cmd_name)
                if callback == False:
                    self._msg(nick, "Unknown command.")
                else:
                    callback(self, nick, chan, cmd_args)
            except:
                traceback.print_exc()

    def nick(self, msg):
        oldnick = msg["host"].split('!')[0]
        newnick = msg["arg"][1:]
        if oldnick in self.admins:
            self.admins[self.admins.index(oldnick)] = newnick
            
    def _msg(self, chan, msg):
        """ Send message to channel """
        self._send("PRIVMSG %s :%s" % (chan, msg))

    def joinchans(self):
        """ Join channels specified in the config file """
        for chan in self.jchans:
            self._send("JOIN %s" % (chan))
                
    def senduser(self):
        """ Send the user message to the IRC server """
        self._send("USER %s * * :%s" % (config["nick"], config["real"]))

    def login(self, nick):
        self.admins.append(nick)

    def sendnick(self):
        """ Send the nick message to the IRC server """
        self._send("NICK %s" % (config["nick"]))

    def _send(self, data):
        """ Send raw data to the IRC server """
        utils.secs.send_data(self.sock, data)
    
    def gracefully_terminate(self):
        """ Gracefully terminate the bot """
        self._send("QUIT :Being terminated")
        self.running = False

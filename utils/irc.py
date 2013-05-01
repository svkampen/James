""" 
IRC API - irc.py
"""

import sys
from .buffer import Buffer
from . import parse
import socket
from .num import NUM as numerics
import time

CONFIG = {}

class IRCHandler(object):
    """ IRCHandler(Dict<string, object> config) - a standard IRC handler """
    def __init__(self, bconfig):
        globals()["CONFIG"] = bconfig
        self.sock = socket.socket()
        
        self.running = True
        self.buff = Buffer()
        self.is_welcome = False

    def connect(self):
        """ Connect to the IRC server and start the main loop """
        server = CONFIG["server"]
        self.sock.connect((server[:-5], int(server[-4:])))
        self.mainloop()

    def mainloop(self):
        """ The main loop. """
        loops = 0
        try:
            while self.running:
                time.sleep(0.1)
                try:
                    self.buff.append(self.sock.recv(1024).decode('utf-8'))
                except UnicodeDecodeError:
                    try:
                        self.buff.append(self.sock.recv(1024).decode('utf-16'))
                    except:
                        pass
                if loops == 0:
                    self.sendnick()
                    self.senduser()
                for msg in self.buff:
                    pmsg = parse.parse(msg)
                    if pmsg['method'] == 'PING':
                        self._send("PONG "+pmsg["arg"])
                    elif pmsg["method"] == "376":
                        self.is_welcome = True
                        self.try_to_call('welcome', args=pmsg)
                    else:
                        if not pmsg['method'].isdigit():
                            self.try_to_call(pmsg['method'].lower(), args=pmsg)
                        else:
                            func = numerics.get(pmsg['method'], False)
                            if func:
                                self.try_to_call(func, args=pmsg)
                loops += 1
        except KeyboardInterrupt:
            sys.exit()

    def _send(self, data, newline='\r\n', sock=None):
        """ Send data through the socket and append CRLF. """
        if sock == None:
            sock = self.sock
        sock.send((data+newline).encode('utf-8'))

    def try_to_call(self, function, namespace=None, args=None, unpack=True):
        """ Try to call a function. """
        if not namespace:
            namespace = self
        if hasattr(namespace, function):
            if not args:
                getattr(namespace, function)()
            else:
                if type(args) not in (tuple, list) or unpack == False:
                    getattr(namespace, function)(args)
                else:
                    getattr(namespace, function)(*args)

    def senduser(self):
        """ Send the IRC USER message. """
        self._send("USER %s * * :%s" % (CONFIG["nick"], CONFIG["real"]))

    def sendnick(self):
        """ Send the IRC NICK message. """
        self._send("NICK %s" % (CONFIG["nick"]))

    def gracefully_terminate(self):
        """ Gracefully terminate the bot. """
        self._send("QUIT :TelnetIRC version 2.7.2")
        self.running = False

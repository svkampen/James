""" 
IRC API - irc.py
"""

import sys
import re
from . import buffer
from . import parse
import socket
from .num import num as numerics

config = {}
is_debugging = False

class IRCHandler(object):
    """ IRCHandler(Dict<string, object> config) - a standard IRC handler """
    def __init__(self, bconfig):
        globals()["config"] = bconfig
        self.sock = socket.socket()
        
        self.running = True
        self.buff = buffer.Buffer()
        self.is_welcome = False

    def connect(self):
        server = config["server"]
        self.sock.connect((server[:-5], int(server[-4:])))
        self.mainloop()

    def mainloop(self):
        loops = 0
        try:
            while self.running and self.buff.append(self.sock.recv(1024).decode('utf-8')):
                if loops == 0:
                    self.sendnick()
                    self.senduser()
                for msg in self.buff:
                    pmsg = parse(msg)
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
                            if func: self.try_to_call(func, args=pmsg)
                loops += 1
        except KeyboardInterrupt:
            sys.exit()

    def _send(self, data, newline='\r\n', sock=None):
        if sock == None:
            sock = self.sock
        sock.send((data+newline).encode('utf-8'))

    def try_to_call(self, function, namespace=None, args=None, unpack=True):
        if not namespace:
            namespace = self
        if hasattr(namespace, function):
            if not args:
                getattr(namespace, function)()
            else:
                if type(args) != list and type(args) != tuple or unpack == False:
                    getattr(namespace, function)(args)
                else:
                    getattr(namespace, function)(*args)

    def senduser(self):
        self._send("USER %s * * :%s" % (config["nick"], config["real"]))

    def sendnick(self):
        self._send("NICK %s" % (config["nick"]))

    def gracefully_terminate(self):
        self._send("QUIT :TelnetIRC version 2.7.2")
        self.running = False

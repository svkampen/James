"""
IRC API - irc.py
"""

import sys
import collections
import inspect
from .buffer import Buffer
from . import parse
import socket
from .num import NUM as numerics
import time
import _thread
import traceback

CONFIG = {}

class IRCHandler(object):
    """ IRCHandler(Dict<string, object> config) - a standard IRC handler """
    def __init__(self, bconfig, verbose=False):
        globals()["CONFIG"] = bconfig
        self.sock = socket.socket()
        self.sockfile = None
        self.verbose = verbose
        self.running = True
        self.buff = Buffer()
        self.outbuff = Buffer()
        self.is_welcome = False

    def connect(self):
        """ Connect to the IRC server and start the main loop """
        server = CONFIG["server"].split("|")[0].split(":")
        self.sock.connect((server[0], int(server[1])))
        try:
            passwd = CONFIG["server"].split("|", 1)[1]
            if passwd:
                self._send("PASS "+passwd)
        except:
            pass
        self.mainloop()

    def mainloop(self):
        """ The main loop. """
        loops = 0
        try:
            while self.running:
                if loops != 0:
                    data = self.sockfile.readline().decode('utf-8', errors='ignore')
                    if not data:
                        self.running = False
                    self.buff.append(data)
                else:
                    self.sockfile = self.sock.makefile("rb")
                    self.sendnick()
                    self.senduser()

                for msg in self.buff:
                    if self.verbose:
                        print(">>> "+msg)
                    pmsg = parse.parse(msg)
                    if pmsg["method"] == "PING":
                        self._send("PONG "+pmsg["arg"])
                    elif pmsg["method"] in ("376", "422"):
                        self.is_welcome = True
                        self.try_to_call("welcome", args=pmsg)
                    else:
                        if not pmsg["method"].isdigit():
                            self.try_to_call(pmsg["method"].lower(), args=pmsg)
                        else:
                            func = numerics.get(pmsg["method"], False)
                            if func:
                                self.try_to_call(func, args=pmsg)

                loops += 1
        except KeyboardInterrupt:
            sys.exit()

    def register_callbacks(self):
        self.__irccallbacks__ = collections.defaultdict(list)

        # get a list of all methods in this (sub)class.
        functions = list(dict(inspect.getmembers(self, predicate=inspect.ismethod)).values())

        for function in functions:
            if hasattr(function, "_callbackhooks"):
                for item in function._callbackhooks:
                    self.__irccallbacks__[item].append(function)

    def register_callback(self, ctype, callback):
        self.__irccallbacks__[ctype].append(callback)


    def _send(self, data, newline="\r\n", sock=None):
        """ Send data through the socket and append CRLF. """
        self.outbuff.append(data+newline)
        for msg in self.outbuff:
            if self.verbose:
                print("<<< "+msg)
            self.sock.send((msg+newline).encode("utf-8"))

    def try_to_call(self, function, namespace=None, args=None, unpack=True):
        """ Try to call a function. """
        if not namespace:
            namespace = self
        if hasattr(namespace, function):
            if not args:
                getattr(namespace, function)()
            else:
                if type(args) not in (tuple, list) or not unpack:
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
        self._send("QUIT :The James IRC Framework v%s" % (self.version))
        self.running = False

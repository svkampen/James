""" 
It is clojure time.
"""

from .util.decorators import command, initializer
import socket, time
from threading import Thread

@initializer
def plugin_initializer(bot):
    globals()['port'] = -1

@command("clojure.set_port")
def set_clojure_port(bot, nick, target, chan, arg):
    try:
        globals()['port'] = int(arg)
    except ValueError:
        bot.msg(chan, "Dammit you! Enter a valid port!")

@command("clojure.eval", short="user=>")
def eval_clojure(bot, nick, target, chan, arg):
    if globals()['port'] == -1:
        bot.msg(chan, "Port for leiningen repl isn't configured!")
    ClojureThread(bot, chan, globals()['port'], arg).start()

class ClojureThread(Thread):
    def __init__(self, bot, chan, port, arg):
        super().__init__()
        self.port = port
        self.arg = arg
        self.chan = chan
        self.bot = bot
     
    def run(self):
        sock = socket.socket()
        sock.connect(("localhost", self.port))
        sock.recv(1024) # throw some data into the void
        sock.send(self.arg.encode('ascii')+'\r\n'.encode('ascii'))
        reply = sock.recv(1024)
        reply = reply.decode('ascii')
        reply = reply.split('\n')[:-1]
        reply = ' '.join(reply)

        self.bot.msg(self.chan, reply.replace("nil", ""))
        time.sleep(10)
        sock.close()

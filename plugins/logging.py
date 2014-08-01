"""
Logging module
"""

from .util.decorators import initializer
import time
import sys
import os

logfile = None

@initializer
def plugin_init(bot):
    global logfile
    output = "%s/james.log" % os.getcwd()
    logfile = open(output, "a", encoding="utf-8")
    for event in bot.state.events.values():
        event.register(logger)

def close_log(*args):
    logfile.close()

def log(data):
    """ log and print data """
    timestamp = time.strftime("[%Y-%d-%m %H:%M:%S] ")
    if sys.stdout != sys.__stdout__:
        sys.__stdout__.write((timestamp+data+"\n").encode("utf-8").decode("utf-8"))
    else:
        try:
            print((timestamp+data).encode("utf-8").decode("utf-8"))
        except:
            pass
    if not logfile.closed:
        logfile.write(timestamp+data+"\n")

def log_message(*args):
    nick = args[1]
    chan = args[2]
    msg = args[-1] # or 3
    ws = " "*(30 - len("[%s]" % (chan)))
    log("[%s]%s<%s> %s" % (chan, ws, nick, msg))


def log_join(*args):
    user = args[1]
    chan = args[2]
    ws = " "*(30 - len("[%s]" % (chan)))
    log("[%s]%sJOIN %s" % (chan, ws, user))

def log_part(*args):
    user = args[1]
    chan = args[2]
    ws = " "*(30 - len("[%s]" % (chan)))
    log("[%s]%sPART %s" % (chan, ws, user))

def log_kick(*args):
    (bot, user, chan) = args
    ws = " "*(30 - len("[%s]" % (chan)))
    log("[%s]%sKICK %s" % (chan, ws, user))

def log_notice(*args):
    sender = args[1]
    args = args[2]
    ws = " "*(30 - len("-%s-" % (sender)))
    log("-%s-%s%s" % (sender, ws, args))

def logger(*args, **kwargs):
    etype = kwargs["type"]
    handlers = {"message": log_message,
     "join": log_join,
     "part": log_part,
     "notice": log_notice,
     "kick": log_kick,
     "shutdown": close_log}
    handlers.get(etype, lambda *args: None)(*args)

    try:
        logfile.flush()
        os.fsync(logfile) 
    except ValueError:
        pass

logger._want_type = True

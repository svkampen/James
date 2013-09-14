"""
Logging module
"""

from .util.decorators import initializer
import time

def close_log(*args):
    logfile.close()

def log(data):
    """ log and print data """
    timestamp = time.strftime("[%H:%M:%S] ")
    try:
        print((timestamp+data).encode('utf-8').decode('utf-8'))
    except:
        pass
    if not logfile.closed:
        logfile.write(timestamp+data+"\n")

def log_message(*args):
    nick = args[1]
    chan = args[2]
    msg = args[-1] # or 3
    ws = " "*(20 - len("[%s]" % (chan)))
    log("[%s]%s<%s> %s" % (chan, ws, nick, msg))


def log_join(*args):
    user = args[1]
    chan = args[2]
    ws = " "*(20 - len("[%s]" % (chan)))
    log("[%s]%sJOIN %s" % (chan, ws, user))

def log_part(*args):
    user = args[1]
    chan = args[2]
    ws = " "*(20 - len("[%s]" % (chan)))
    log("[%s]%sPART %s" % (chan, ws, user))

def log_welcome(*args):
    log("Server has welcomed us.")

def log_kick(*args):
    (bot, user, chan) = args
    ws = " "*(20 - len("[%s]" % (chan)))
    log("[%s]%sKICK %s" % (chan, ws, user))

def log_notice(*args):
    sender = args[1]
    args = args[2]
    ws = " "*(20 - len("-%s-" % (sender)))
    log("-%s-%s%s" % (sender, ws, args))

def logger(*args, **kwargs):
    etype = kwargs['type']
    handlers = {'message': log_message,
     'join': log_join,
     'part': log_part,
     'welcome': log_welcome,
     'notice': log_notice,
     'kick': log_kick,
     'close_log': close_log}
    handlers.get(etype, lambda *args: None)(*args)

logger._want_type = True

@initializer
def plugin_init(bot):
    global logfile
    output = "%s/james.log" % bot.botdir
    logfile = open(output, 'a', encoding='utf-8')
    for event in bot.state.events.values():
        event.register(logger)
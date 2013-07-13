"""
Logging module
"""

from .util.decorators import initializer
import time

def log(data):
    """ log and print data """
    timestamp = time.strftime("[%H:%M:%S] ")
    try:
        print((timestamp+data).encode('utf-8').decode('utf-8'))
    except:
        pass
    logfile.write(timestamp+data+"\n")

def log_message(*args):
    nick = args[1]
    chan = args[3]
    msg = args[-1] # or 4
    log("[%s] <%s> %s" % (chan, nick, msg))


def log_join(*args):
    user = args[1]
    chan = args[2]
    log("[%s] JOIN %s" % (chan, user))

def log_part(*args):
    user = args[1]
    chan = args[2]
    log("[%s] PART %s" % (chan, user))

def log_welcome(*args):
    log("Server has welcomed us.")

def log_notice(*args):
    sender = args[1]
    args = args[2]
    log("-%s- %s" % (sender, args))


def logger(*args, **kwargs):
    etype = kwargs['type']
    handlers = {'message': log_message,
     'join': log_join,
     'part': log_part,
     'welcome': log_welcome,
     'notice': log_notice}
    handlers.get(etype, lambda gs: None)(*args)

@initializer
def plugin_init(bot):
    global logfile
    output = "%s/james.log" % bot.botdir
    logfile = open(output, 'a', encoding='utf-8')
    for event in bot.state.events.values():
        event.register(logger)
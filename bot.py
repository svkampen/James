#!/usr/bin/env python3
""" 
James.py - main bot
"""

from utils.irc import IRCHandler
import utils
import traceback
import re
import os
import sys
import json
import plugins
import functools
from collections import deque
import utils.logging as logging
from utils.commandhandler import CommandHandler
from utils.events import Event
from utils.decorators import startinfo, sethook

CONFIG = {}
VERSION = "3.5 prerelease"

class James(IRCHandler):
    """ James main bot executable thingy class """
    @startinfo(VERSION)
    def __init__(self, config, verbose=False):
        super(James, self).__init__(config, verbose=verbose)
        globals()['CONFIG'] = config

        self.version = VERSION

        # Bot state and logger.
        self.state = utils.ServerState()
        self.log = logging.Logger()

        # state.
        self.state.events = self.initialize_events()
        self.state.apikeys = json.loads(open('apikeys.conf').read())
        self.state.data = {'autojoin_channels': []}
        self.state.data['autojoin_channels'].extend(CONFIG['autojoin'])
        for entry in CONFIG['admins']:
            self.state.admins.add(entry.lower())
        self.state.nick = CONFIG['nick']

        # Various things
        self.lastmsgof = {}
        self.cmdhandler = CommandHandler(self, plugins.get_plugins())
        self.leo = object() # Last eval output
        
        self.set_up_partials()

    def set_up_partials(self):
        utils.parse.inline_python = functools.partial(utils.parse.inline_python, self)

    def initialize_events(self):
        return {item:Event() for item in utils.events.StandardEvents}

    def welcome(self, msg: dict):
        """ welcome(msg) - handles on-login actions """
        if CONFIG['ident_pass']:
            self.msg(CONFIG['identify_service'], 'identify %s' % (CONFIG['ident_pass']))
        self._send("MODE %s +B" % (self.state.nick))
        self.state.events['WelcomeEvent'].fire(self)

    def notice(self, msg):
        actualargs = msg['arg'].split(' ',1)[1][1:]
        sender = msg['host'].split('!')[0]
        self.state.notices.append({'sender': sender, 'message': actualargs})
        self.log.log("-%s- %s" % (sender, actualargs))
        
    def privmsg(self, msg):
        """ Handles messages """
        # Split msg into parts
        nick = msg['host'].split('!')[0] #get sender
        chan = msg['arg'].split()[0] #get chan
        if chan == self.state.nick:
            chan = nick #if chan is us, file under them
        chan = chan.lower()
        rawmsg = msg['arg'].split(':', 1)[1] #get msg
        target = nick #failsafe

        if nick.lower() in self.state.muted and chan.startswith('#'):
            return self.log.log("[%s] <%s> %s" % (chan, nick, rawmsg))

        # Test for target
        msg = rawmsg
        try:
            if ',' in rawmsg:
                preamb = rawmsg.split(',')[0]
                if preamb.lower() in self.lastmsgof[chan].keys(): # CHANGE THIS - Hackish solution
                    target = preamb
                    msg = rawmsg.split(',', 1)[1].lstrip()
            if ':' in rawmsg:
                preamb = rawmsg.split(':')[0]
                if preamb.lower() in self.lastmsgof[chan].keys(): # These should check user lists, not lastmsgof keys
                    target = preamb
                    msg = rawmsg.split(':', 1)[1].lstrip()
        except KeyError:
            if chan in self.lastmsgof.keys():
                self.lastmsgof[chan.lower()][nick.lower()] = deque([rawmsg], 16)
            else:
                self.lastmsgof[chan.lower()] = {nick: deque([rawmsg], 16)}

        self.log.log("[%s] <%s> %s" % (chan, nick, rawmsg))
        self.handlemsg(nick, chan, msg, target, rawmsg)

    def handlemsg(self, nick, chan, msg, target, rawmsg):
        """ Handles Messages """
        # Test for inline code
        msg = utils.parse.inline_python(nick, chan, msg)

        # Test for sed
        try:
            if utils.parse.check_for_sed(self, msg):
                parsed_msg = utils.parse.parse_sed(self, msg.replace("\/", "\13"), self.lastmsgof[chan.lower()][target.lower()])
                if parsed_msg == -1:
                    self._msg(chan, "%s: No matches found" % (nick))
                else:
                    new_msg = re.sub(parsed_msg['to_replace'], parsed_msg['replacement'], parsed_msg['oldmsg'], 0 if parsed_msg['glob'] else 1)
                    if not '\x01' in new_msg:
                        self._msg(chan, "<%s> %s" % (target, new_msg.replace("\13", "/")))
                    else:
                        self._msg(chan, "*%s %s*" % (target, new_msg.replace('\13', '/').split('\x01')[1].split(' ', 1)[1]))
            else:
                self.lastmsgof[chan.lower()][nick.lower()].appendleft(rawmsg)

        except KeyError:
            if chan.lower() in self.lastmsgof.keys():
                self.lastmsgof[chan.lower()][nick.lower()] = deque([rawmsg], 16)
            else:
                self.lastmsgof[chan.lower()] = {nick: deque([rawmsg], 16)}

        # Test for command
        self.check_for_command(msg, nick, target, chan)

        self.state.events['MessageEvent'].fire(self, nick, target, chan, msg)

    def check_for_command(self, msg, nick, target, chan):
        """ Check for a normal command starting with the command char. """
        cmd_splitmsg = msg.split(" ", 1)
        try:
            if len(cmd_splitmsg) > 1:
                cmd_args = cmd_splitmsg[1]
            else:
                cmd_args = ''

            triggered_short = self.cmdhandler.trigger_short(cmd_splitmsg[0])
            if triggered_short:
                if hasattr(triggered_short.function, "_require_admin"):
                    if nick.lower() in self.state.admins:
                        triggered_short(self, nick, target, chan, cmd_args)
                else:
                    triggered_short(self, nick, target, chan, cmd_args)
            if msg.startswith(CONFIG['cmdchar']):
                cmd_name = cmd_splitmsg[0][1:]
                callback = self.cmdhandler.trigger(cmd_name)
                
                if not callback: return

                if hasattr(callback.function, '_require_admin'):
                    if nick.lower() in self.state.admins:
                        callback(self, nick, target, chan, cmd_args)
                else:
                    callback(self, nick, target, chan, cmd_args)
        except BaseException:
            self._meditate(sys.exc_info(), chan)
            traceback.print_exc()
                
    def _meditate(self, exc_info, chan):
        """ Prints GURU MEDITATION messages - at least, it used to. """
        exc_name = str(exc_info[0]).split("'")[1]
        exc_args = exc_info[1].args
        if exc_args:
            self._msg(chan, \
                      "[\x02\x034GURU\x03 MEDITATION\x034\x03 %s\x02] %s"\
                      % (exc_name, exc_args[0]))
        else:
            self._msg(chan, \
                      "[\x02\x034GURU\x03 MEDITATION\x034\x03 %s\x02]"\
                      % (exc_name))

    def nick(self, msg):
        """ Handles nickchanges """
        oldnick = msg['host'].split('!')[0]
        newnick = msg['arg'][1:]
        if oldnick.lower() in self.state.admins:
            self.admins.muted.remove(oldnick.lower())
            self.admins.muted.add(newnick.lower())
        if oldnick.lower() in self.state.muted:
            self.state.muted.remove(oldnick.lower())
            self.state.muted.add(newnick.lower())

    def join(self, msg):
        """ Handles people joining channels """
        user = msg['host'].split('!')[0].strip().lower()
        channel = msg['arg'][1:].strip().lower()
        self.state.events['JoinEvent'].fire(self, user, channel)
        self.log.log("[%s] JOIN %s" % (channel, user))

    def part(self, msg):
        """ Handles people parting channels """
        channel = msg['arg'].split()[0].strip().lower()
        user = msg['host'].split('!')[0].strip().lower()
        try:
            self.log.log("[%s] PART %s" % (channel, user))
        except BaseException:
            traceback.print_exc()

    def _msg(self, chan, msg):
        """ _msg(string chan, string msg) - Sends a PRIVMSG. """
        msg = str(msg)
        if '\n' in msg:
            for item in msg.split('\n'):
                self._send("PRIVMSG %s :%s" % (chan, item))
        else:
            self._send("PRIVMSG %s :%s" % (chan, msg))

    def msg(self, chan, msg):
        """ msg(string chan, string msg) - Sends a PRIVMSG. """
        self._msg(chan, msg)

    def gracefully_terminate(self):
        """ Handles the quit routine, then exits. """
        try:
            super(James, self).gracefully_terminate()
        except SystemExit:
            pass
        self.log.close()


if __name__ == '__main__':
    ARGS = sys.argv[1:]
    CONFIG = json.loads(open('config.json', 'r').readline())
    if '--verbose' in ARGS:
        BOT = James(CONFIG, verbose=True)
    else:
        BOT = James(CONFIG)
    BOT.connect()
else:
    my_globals = globals()


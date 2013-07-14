#!/usr/bin/env python3
"""
James.py - main bot
"""

from utils.irc import IRCHandler
import utils
import os
import traceback
import re
import sys
import json
import plugins
import functools
from collections import deque
from utils.commandhandler import CommandHandler
from utils.events import Event
from utils.decorators import startinfo

CONFIG = {}
VERSION = "4b2"


class James(IRCHandler):
    """ James main bot executable thingy class """
    @startinfo(VERSION)
    def __init__(self, config, verbose=False):
        super(James, self).__init__(config, verbose=verbose)
        globals()['CONFIG'] = config

        self.version = VERSION

        # Bot state and logger.
        self.state = utils.ServerState()
        self.botdir = os.getcwd()

        # state.
        self.state.events = {list(i.keys())[0]: Event(list(i.values())[0])
            for i in utils.events.Standard}

        self.state.apikeys = json.loads(open('apikeys.conf').read())
        self.state.data = {'autojoin_channels': []}
        self.state.data['autojoin_channels'].extend(CONFIG['autojoin'])
        for entry in CONFIG['admins']:
            self.state.admins.add(entry.lower())
        self.state.nick = CONFIG['nick']

        # Various things
        self.lastmsgof = {}
        self.cmdhandler = CommandHandler(self, plugins.get_plugins())
        self.leo = object()  # Last eval output

        self.set_up_partials()

    def set_up_partials(self):
        """Set up partial functions"""
        ip = utils.parse.inline_python
        utils.parse.inline_python = functools.partial(ip, self)

    def welcome(self, *args):
        """ welcome(msg) - handles on-login actions """
        if CONFIG['ident_pass']:
            self.msg(CONFIG['identify_service'], 'identify %s'
                % (CONFIG['ident_pass']))
        self._send("MODE %s +B" % (self.state.nick))
        self.state.events['WelcomeEvent'].fire(self)

    def notice(self, msg):
        """ Handle notices """
        actualargs = msg['arg'].split(' ', 1)[1][1:]
        sender = msg['host'].split('!')[0]
        self.state.notices.append({'sender': sender, 'message': actualargs})
        #self.log.log("-%s- %s" % (sender, actualargs))
        self.state.events['NoticeEvent'].fire(self, sender, actualargs)

    def privmsg(self, msg):
        """ Handles messages """
        # Split msg into parts
        nick = msg['host'].split('!')[0]  # get sender
        chan = msg['arg'].split()[0]  # get chan
        if not chan.startswith('#'):
            chan = nick  # if chan is a private message, file under them
        chan = chan.lower()
        rawmsg = msg['arg'].split(':', 1)[1]  # get msg
        target = nick

        if nick.lower() in self.state.muted and chan.startswith('#'):
            return self.state.events['MessageEvent'].fire(self, nick, None, chan, rawmsg)

        self.handlemsg(nick, chan, msg, target, rawmsg)

    def handlemsg(self, nick, chan, msg, target, rawmsg):
        """ Handles Messages.. again """
        # Test for inline code
        msg = utils.parse.inline_python(nick, chan, msg)
        self.check_for_command(msg, nick, target, chan)

        self.state.events['MessageEvent'].fire(self, nick, target, chan, msg)

    def check_for_command(self, msg, nick, target, chan):
        """ Check for a command """
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

                if not callback:
                    return

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
            self._msg(chan,
                      "[\x02\x034GURU\x03 MEDITATION\x034\x03 %s\x02] %s"
                      % (exc_name, exc_args[0]))
        else:
            self._msg(chan,
                      "[\x02\x034GURU\x03 MEDITATION\x034\x03 %s\x02]"
                      % (exc_name))

    def nick(self, msg):
        """ Handles nickchanges """
        oldnick = msg['host'].split('!')[0]
        newnick = msg['arg'][1:]
        if oldnick.lower() in self.state.admins:
            self.state.admins.remove(oldnick.lower())
            self.state.admins.add(newnick.lower())
        if oldnick.lower() in self.state.muted:
            self.state.muted.remove(oldnick.lower())
            self.state.muted.add(newnick.lower())

    def join(self, msg):
        """ Handles people joining channels """
        user = msg['host'].split('!')[0].strip().lower()
        channel = msg['arg'][1:].strip().lower()
        self.state.events['JoinEvent'].fire(self, user, channel)
        #self.log.log("[%s] JOIN %s" % (channel, user))

    def part(self, msg):
        """ Handles people parting channels """
        channel = msg['arg'].split()[0].strip().lower()
        user = msg['host'].split('!')[0].strip().lower()
        try:
            #self.log.log("[%s] PART %s" % (channel, user))
            self.state.events['PartEvent'].fire(self, user, channel)
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
        self.state.events['CloseLogEvent'].fire()


if __name__ == '__main__':
    ARGS = sys.argv[1:]
    CONFIG = json.loads(open('config.json', 'r').read())
    if '--verbose' in ARGS:
        BOT = James(CONFIG, verbose=True)
    else:
        BOT = James(CONFIG)
    BOT.connect()

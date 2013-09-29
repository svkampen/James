#!/usr/bin/env python3
"""
James.py - main bot
"""

from utils.irc import IRCHandler
from utils.sstate import ServerState
from utils.threads import HandlerThread
from utils.function import Function
import utils
import plugins

import os
import traceback
import re
import sys
import json
import functools

from collections import deque

from utils.commandhandler import CommandHandler
from utils.events import Event
from utils.decorators import startinfo
from utils import is_enabled

CONFIG = {}
VERSION = "5.0.0b2"
MAX_MESSAGE_STORAGE = 256


class James(IRCHandler):
    """ James main bot executable thingy class """
    @startinfo(VERSION)
    def __init__(self, config, verbose=False, debug=False):
        super(James, self).__init__(config, verbose=verbose)
        globals()["CONFIG"] = config

        self.version = VERSION
        self.debug = debug

        # Bot state and logger.
        self.state = ServerState()
        self.botdir = os.getcwd()

        # state.
        self.state.events.update({list(i.keys())[0]: Event(list(i.values())[0])
            for i in utils.events.Standard})

        self.state.apikeys = json.loads(open("apikeys.conf").read())
        self.state.data = {"autojoin_channels": []}
        self.state.data["autojoin_channels"].extend(CONFIG["autojoin"])
        for entry in CONFIG["admins"]:
            self.state.admins.add(entry.lower())
        self.state.nick = CONFIG["nick"]

        # Various things
        self.lastmsgof = {}
        self.cmdhandler = CommandHandler(self, plugins.get_plugins())
        self.leo = object()  # Last eval output
        self.cmd_thread = HandlerThread()
        self.cmd_thread.daemon = True

        self.set_up_partials()

    def __repr__(self):
        return "James(server=%r, channels=%s)" % (CONFIG["server"].split(":")[0], list(self.state.channels.keys()))

    def _meditate(self, exc_info, chan):
        """ Prints GURU MEDITATION messages. """
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

    def _msg(self, chan, msg):
        """ _msg(string chan, string msg) - Sends a PRIVMSG. """
        msg = str(msg)
        if "\n" in msg:
            for item in msg.split("\n"):
                self._send("PRIVMSG %s :%s" % (chan, item))
        else:
            self._send("PRIVMSG %s :%s" % (chan, msg))

    def check_for_command(self, msg, nick, chan):
        """ Check for a command """
        cmd_splitmsg = msg.split(" ", 1)
        try:
            if len(cmd_splitmsg) > 1:
                cmd_args = cmd_splitmsg[1]
            else:
                cmd_args = ""

            triggered_short = self.cmdhandler.trigger_short(cmd_splitmsg[0])
            if not triggered_short or not is_enabled(self, chan, triggered_short):
                triggered_short = False
            if triggered_short and CONFIG["short_enabled"]:
                if hasattr(triggered_short.function, "_require_admin"):
                    if nick.lower() in self.state.admins:
                        self.cmd_thread.handle(Function(
                            triggered_short, (self, nick, chan, cmd_args)))
                else:
                    self.cmd_thread.handle(Function(triggered_short,
                        (self, nick, chan, cmd_args)))

            if msg.startswith(CONFIG["cmdchar"]):
                cmd_name = cmd_splitmsg[0][1:]
                callback = self.cmdhandler.trigger(cmd_name)
                if not callback:
                    return
                if not is_enabled(self, chan, callback):
                    return

                if hasattr(callback.function, "_require_admin"):
                    if nick.lower() in self.state.admins:
                        self.cmd_thread.handle(Function(callback, 
                            (self, nick, chan, cmd_args)))
                else:
                    self.cmd_thread.handle(Function(callback,
                        (self, nick, chan, cmd_args)))
        except BaseException:
            self._meditate(sys.exc_info(), chan)
            traceback.print_exc()

    def cmodes(self, msg):
        modes = msg["arg"].split()[2]
        channel = msg["arg"].split()[1]
        c = self.state.channels.get(channel, False)
        if c:
            c._modes = modes

    def mode(self, msg):
        self.state.nick = msg["arg"].split(" ", 1)[0]

    def connect(self):
        self.cmd_thread.start()
        super().connect()

    def getconfig(self):
        """ Get the botconfig from another module """
        return CONFIG

    def gracefully_terminate(self):
        """ Handles the quit routine, then exits. """
        try:
            super(James, self).gracefully_terminate()
        except SystemExit:
            pass
        self.state.events["CloseLogEvent"].fire()

    def join(self, msg):
        """ Handles people joining channels """
        user = msg["host"].split("!")[0].strip().lower()
        channel = msg["arg"][1:].strip().lower()
        if user == self.state.nick.lower().strip():
            self.state.channels.add(channel)
            self._send("MODE %s" % (channel))
        self.state.channels[channel].add_user(user)
        self.state.events["JoinEvent"].fire(self, user, channel)
        #self.log.log("[%s] JOIN %s" % (channel, user))

    def msg(self, chan, msg):
        """ msg(string chan, string msg) - Sends a PRIVMSG. """
        self._msg(chan, msg)

    def names(self, msg):
        """ Executed on NAMES reply """
        chantype = re.match(r"(=|@|\*).*", msg["arg"].split(" ", 1)[1])
        chantype = chantype.groups()[0]
        args = msg["arg"].split(chantype)[1]
        chan = args.split(":")[0][:-1].strip().lower()
        users = args.split(":")[1].split()
        modes = ["+", "%", "@", "&", "~"]

        users = set([u for u in users if not u[:1] in modes]
            + [u[1:] for u in users if u[:1] in modes])

        channel = self.state.channels.get(chan, False)
        if channel:
            channel.update_users(users)
        else:
            self.state.channels.add(chan)
            self.state.channels[chan].update_users(users)

    def notice(self, msg):
        """ Handle notices """
        actualargs = msg["arg"].split(" ", 1)[1][1:]
        sender = msg["host"].split("!")[0]
        self.state.notices.append({"sender": sender, "message": actualargs})
        self.state.events["NoticeEvent"].fire(self, sender, actualargs)

    def nick(self, msg):
        """ Handles nickchanges """
        oldnick = msg["host"].split("!")[0].lower()
        newnick = msg["arg"][1:].lower()

        if oldnick in self.state.admins:
            self.state.admins.replace(oldnick, newnick)

        if oldnick in self.state.muted:
            self.state.muted.replace(oldnick, newnick)

        if oldnick == self.state.nick:
            self.state.nick = newnick

        for chan in self.state.channels.get_channels_for(oldnick).values():
            chan.change_user((oldnick, newnick))

    def part(self, msg):
        """ Handles people parting channels """
        channel = msg["arg"].split()[0].strip().lower()
        user = msg["host"].split("!")[0].strip().lower()
        self.state.channels[channel].remove_user(user)
        try:
            #self.log.log("[%s] PART %s" % (channel, user))
            self.state.events["PartEvent"].fire(self, user, channel)
        except BaseException:
            traceback.print_exc()

    def privmsg(self, msg):
        """ Handles messages """
        # Split msg into parts
        nick = msg["host"].split("!")[0].lower()  # get sender
        chan = msg["arg"].split()[0]  # get chan
        if not chan.startswith("#"):
            chan = nick  # if chan is a private message, file under them
            self.state.channels.add(chan)
            self.state.channels[chan].update_users({nick})
        chan = chan.lower()
        msg = msg["arg"].split(":", 1)[1]  # get msg

        if nick.lower() in self.state.muted and chan.startswith("#"):
            return self.state.events["MessageEvent"].fire(self, nick, chan, msg)

        # Test for inline code
        msg = utils.parse.inline_python(nick, chan, msg)

        if CONFIG["sed-enabled"]:
            utils.parse.sed(self, nick, chan, msg)

        self.check_for_command(msg, nick, chan)

        self.state.events["MessageEvent"].fire(self, nick, chan, msg)

        msg = utils.message.Message(nick, self.state.channels[chan], msg)
        if nick in self.state.messages.keys():
            self.state.messages[nick].appendleft(msg)
        else:
            self.state.messages[nick] = deque([msg], MAX_MESSAGE_STORAGE)

    def quit(self, msg):
        nick = msg["host"].split("!")[0].lower()
        for channel in self.state.channels.get_channels_for(nick).values():
            channel.remove_user(nick)
        if self.state.users.get(nick, False):
            del self.state.users[nick]

    def kick(self, msg):
        nick = msg["arg"].split()[1].lower()
        chan = msg["arg"].split()[0].lower()
        channel = self.state.channels.get(chan, False)
        if channel:
            channel.remove_user(nick)
        self.state.events["KickEvent"].fire(self, nick, chan)


    def set_up_partials(self):
        """Set up partial functions"""
        ip = utils.parse.inline_python
        utils.parse.inline_python = functools.partial(ip, self)

    def welcome(self, *args):
        """ welcome(msg) - handles on-login actions """
        if CONFIG["ident_pass"]:
            self.msg(CONFIG["identify_service"], "identify %s"
                % (CONFIG["ident_pass"]))
        self._send("MODE %s +B" % (self.state.nick))
        self.state.events["WelcomeEvent"].fire(self)



if __name__ == "__main__":
    if (sys.getdefaultencoding() == "ascii" or sys.getfilesystemencoding() == "ascii"):
        raise OSError("Your shitty OS uses ASCII as its default (FS) encoding. Fix it.")
    
    ARGS = sys.argv[1:]
    CONFIG = json.loads(open("config.json", "r").read())
    
    VERBOSE = False
    DEBUG = False

    if "--verbose" in ARGS:
        VERBOSE = True
    if "--debug" in ARGS:
        DEBUG = True

    BOT = James(CONFIG, VERBOSE, DEBUG)
    BOT.connect()

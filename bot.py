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
import threading

from collections import deque

from utils.commandhandler import CommandHandler
from utils.events import Event
from utils.decorators import startinfo
from utils import is_enabled

VERSION = "5.1.0"
MAX_MESSAGE_STORAGE = 256


class James(IRCHandler):
    """ James main bot executable thingy class """
    @startinfo(VERSION)
    def __init__(self, config, verbose=False, debug=False):
        super(James, self).__init__(config, verbose=verbose)

        self.version = VERSION
        self.debug = debug

        # Bot state and logger.
        self.state = ServerState()
        self.botdir = os.getcwd()
        self.config = config
        self.manager = None
        self.id = None

        # state.
        self.state.events.update({list(i.keys())[0]: Event(list(i.values())[0])
            for i in utils.events.Standard})

        self.state.apikeys = json.loads(open("apikeys.conf").read())
        self.state.data = {"autojoin_channels": []}
        self.state.data["autojoin_channels"].extend(self.config["autojoin"])
        for entry in self.config["admins"]:
            self.state.admins.add(entry.lower())
        self.state.nick = self.config["nick"]

        # Various things
        self.cmdhandler = CommandHandler(self, plugins.get_plugins())
        self.cmd_thread = HandlerThread()
        self.cmd_thread.daemon = True

    def __repr__(self):
        return "James(server=%r, chans=%s)" % (self.config["server"].split(":")[0],
                list(self.state.channels.keys()))

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

    def _check_for_command(self, msg, nick, chan):
        """ Check for a command """
        cmd_splitmsg = msg.split(" ", 1)
        try:
            if len(cmd_splitmsg) > 1:
                cmd_args = cmd_splitmsg[1]
            else:
                cmd_args = ""

            trig_short = self.cmdhandler.trigger_short(cmd_splitmsg[0])
            if not trig_short or not is_enabled(self, chan, trig_short):
                trig_short = None
            if trig_short and self.config["short_enabled"]:
                if hasattr(trig_short.function, "_require_admin"):
                    if nick.lower() in self.state.admins:
                        self.cmd_thread.handle(Function(
                            trig_short, (self, nick, chan, cmd_args)))
                else:
                    self.cmd_thread.handle(Function(trig_short,
                        (self, nick, chan, cmd_args)))

            if msg.startswith(self.config["cmdchar"]):
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
        """ channel mode handler. """
        modes = msg["arg"].split()[2]
        channel = msg["arg"].split()[1]
        chan = self.state.channels.get(channel, False)
        if chan:
            chan.modes_ = modes

    @staticmethod
    def ctcp(msg):
        return "\x01%s\x01" % (msg)

    def mode(self, msg):
        """ Handle MODE. """
        if not msg["arg"].startswith("#"):
            self.state.nick = msg["arg"].split(" ", 1)[0]
            print("Set self.state.nick to %s" % (self.state.nick))

    def connect(self):
        self.cmd_thread.start()
        super().connect()


    def getconfig(self):
        """ Get the botconfig from another module """
        return self.config

    def gracefully_terminate(self):
        """ Handles the quit routine, then exits. """
        try:
            super(James, self).gracefully_terminate()
        except SystemExit:
            pass
        self.manager.bots.remove(self)
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
        """ Handles people parting channels. """
        channel = msg["arg"].split()[0].strip().lower()
        user = msg["host"].split("!")[0].strip().lower()
        self.state.channels[channel].remove_user(user)
        try:
            #self.log.log("[%s] PART %s" % (channel, user))
            self.state.events["PartEvent"].fire(self, user, channel)
        except BaseException:
            traceback.print_exc()

    def privmsg(self, msg):
        """ Handles messages. """
        # Split msg into parts
        nick = msg["host"].split("!")[0].lower()  # get sender
        nick_exact = msg["host"].split("!")[0]
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
        # msg = utils.parse.inline_python(self, nick, chan, msg)

        if self.config["sed-enabled"]:
            utils.parse.sed(self, nick, chan, msg)

        self._check_for_command(msg, nick, chan)

        self.state.events["MessageEvent"].fire(self, nick, chan, msg)

        msg = utils.message.Message(nick, self.state.channels[chan], msg)
        if nick in self.state.messages.keys():
            self.state.messages[nick].appendleft(msg)
        else:
            self.state.messages[nick] = deque([msg], MAX_MESSAGE_STORAGE)
        try:
            self.state.users[nick].exactnick = nick_exact
        except:
            pass

        if self != self.manager.main_bot:
            try:
                self.manager.main_bot.msg("#base", "[%s:%s] <%s> %s" % (self.config["server"], chan, nick, msg.msg))
            except BrokenPipeError:
                self.manager.main_bot = self

    def quit(self, msg):
        """ Handles quits. """
        nick = msg["host"].split("!")[0].lower()
        for channel in self.state.channels.get_channels_for(nick).values():
            channel.remove_user(nick)
        if self.state.users.get(nick, False):
            del self.state.users[nick]

    def kick(self, msg):
        """ Handles kicks. """
        nick = msg["arg"].split()[1].lower()
        chan = msg["arg"].split()[0].lower()
        channel = self.state.channels.get(chan, False)
        if channel:
            channel.remove_user(nick)
        self.state.events["KickEvent"].fire(self, nick, chan)

    def welcome(self, *args):
        """ welcome(msg) - handles on-login actions """
        if self.config["ident_pass"]:
            self.msg(self.config["identify_service"], "identify %s"
                % (self.config["ident_pass"]))
        self._send("MODE %s +B" % (self.state.nick))
        self.state.events["WelcomeEvent"].fire(self)



class BotManager():
    def __init__(self):
        self.bots = deque()
        self.bot_threads = deque()

    def get_bot_by_server(self, server):
        for bot in self.bots:
            if server in repr(bot):
                return bot

    def shutdown_bot(self, bot):
        bot.gracefully_terminate()
        for thread in self.bot_threads:
            if thread._stopped:
                self.bot_threads.remove(thread)

    def start_bot(self, bot):
        self.bots.append(bot)
        thr = threading.Thread(target=bot.connect)
        thr.name = repr(bot)
        thr.daemon = False
        self.bot_threads.append(thr)
        thr.start()



if __name__ == "__main__":
    ARGS = sys.argv[1:]
    config = json.loads(open("config.json", "r").read())

    VERBOSE = False
    DEBUG = False

    if "--verbose" in ARGS:
        VERBOSE = True
    if "--debug" in ARGS:
        DEBUG = True

    manager = BotManager()

    BOT = James(config, VERBOSE, DEBUG)
    BOT.manager = manager
    manager.main_bot = BOT
    manager.start_bot(BOT)
    

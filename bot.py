#!/usr/bin/env python3
import sys
"""
James.py - main bot
"""

import utils
from utils.irc import IRCHandler
from utils.sstate import ServerState
from utils.threads import HandlerThread
from utils.style import Styler
from functools import partial
import plugins

import traceback
import re
import ssl
import sys
import json
import threading

from collections import deque

from utils.commandhandler import CommandHandler
from utils.events import Event
from utils.decorators import startinfo, IRCCallback

VERSION = "5.3.3"
MAX_MESSAGE_STORAGE = 256


class James(IRCHandler):
    """ James main bot executable thingy class """
    @startinfo(VERSION)
    def __init__(self, config, verbose=False, debug=False):
        super(James, self).__init__(config, verbose=verbose)

        self.version = VERSION
        self.debug = debug

        # Bot state and logger.
        self.state = ServerState(self)
        self.config = config
        self.style = Styler()
        self.defaultcolor = self.style.gray
        self.hicolor = self.style.pink

        # event stuff
        self.state.events.update({list(i.keys())[0]: Event(list(i.values())[0])
            for i in utils.events.Standard})

        self.state.apikeys = json.loads(open("apikeys.conf").read())
        self.state.data = {"autojoin_channels": []}
        self.state.data["autojoin_channels"].extend(self.config["autojoin"])
        for entry in self.config["admins"]:
            self.state.admins.add(entry.lower())
        self.state.nick = self.config["nick"]

        for user in self.config["muted"]:
            self.state.mute(user)

        # Various things
        self.cmdhandler = CommandHandler(self, plugins.get_plugins())
        self.cmd_thread = HandlerThread(self)
        self.cmd_thread.daemon = True

        self.state.messages[self.state.nick] = deque([], MAX_MESSAGE_STORAGE)
        self.register_callbacks()

    def __repr__(self):
        return ("James(server=%r, chans=%s)"
            % (self.config["server"].split(":")[0],
               list(self.state.channels.keys())))

    def _msg(self, chan, msg):
        """ _msg(string chan, string msg) - Sends a PRIVMSG. """
        msg = str(msg).replace("\r", "").replace("\x07", "")
        if "\n" in msg:
            for item in msg.split("\n"):
                self._msg(chan, item)
                try:
                    mesg = utils.message.Message(self.state.nick, self.state.channels[chan], item)
                    self.state.messages[self.state.nick].appendleft(mesg)
                except:
                    pass
        else:
            self._send("PRIVMSG %s :%s" % (chan, msg))
            try:
                mesg = utils.message.Message(self.state.nick, self.state.channels[chan], msg)
                self.state.messages[self.state.nick].appendleft(mesg)
            except:
                pass


    def _check_for_command(self, msg, nick, chan):
        """ Check for a command """
        cmd_splitmsg = msg.split(" ", 1)
        if len(cmd_splitmsg) > 1:
            cmd_args = cmd_splitmsg[1]
        else:
            cmd_args = ""

        trig_short = self.cmdhandler.trigger_short(cmd_splitmsg[0])
        if trig_short and self.config["short_enabled"]:
            if hasattr(trig_short.function, "_require_admin"):
                if nick.lower() in self.state.admins:
                    self.cmd_thread.handle(partial(trig_short,
                        self, nick, chan, cmd_args))
                    self.state.events["CommandCalledEvent"].fire(self,
                        trig_short, cmd_args)
            else:
                self.cmd_thread.handle(partial(trig_short,
                        self, nick, chan, cmd_args))
                self.state.events["CommandCalledEvent"].fire(self,
                    trig_short, cmd_args)

        if msg.startswith(self.config["cmdchar"]):
            cmd_name = cmd_splitmsg[0][1:]
            callback = self.cmdhandler.trigger(cmd_name)
            if not callback:
                return

            if hasattr(callback.function, "_require_admin"):
                if nick.lower() in self.state.admins:
                    self.cmd_thread.handle(partial(callback,
                        self, nick, chan, cmd_args))
                    self.state.events["CommandCalledEvent"].fire(self,
                        callback, cmd_args)
            else:
                self.cmd_thread.handle(partial(callback,
                        self, nick, chan, cmd_args))
                self.state.events["CommandCalledEvent"].fire(self,
                    callback, cmd_args)

    def _check_for_re_command(self, msg, nick, chan):
        for cmd in self.cmdhandler.commands_with_re:
            match = cmd.is_re_triggered_by(msg)
            if match:
                cmd(self, nick, chan, match.groups())
                self.state.events["CommandCalledEvent"].fire(self,
                    cmd, match.groups())

    @staticmethod
    def ctcp(msg):
        """ Turn a message into a CTCP """
        return "\x01%s\x01" % (msg)

    def set_topic(self, channel, topic):
        self.state.channels[channel].topic = topic
        return self._send("TOPIC %s :%s" % (channel, topic))

    @IRCCallback("MODE")
    def mode(self, msg):
        """ Handle MODE. """
        if not msg["arg"].startswith("#"):
            self.state.nick = msg["arg"].split(" ", 1)[0]

    @IRCCallback("332") # RPL_TOPIC
    def newtopic(self, msg):
        nick, chan, topic = msg["arg"].split(" ", 2)
        topic = topic[1:]
        print(chan)
        print(topic)
        self.state.channels.add(chan)

        self.state.channels[chan].topic = topic

    def connect(self):
        """ Connect the bot to the server """
        self.cmd_thread.start()
        if self.getconfig()["ssl"] == True:
            self.sock = ssl.wrap_socket(self.sock)
        super().connect()

    def getconfig(self):
        """ Get the botconfig from another module """
        return self.config

    def gracefully_terminate(self):
        """ Handles the quit routine, then exits. """
        super(James, self).gracefully_terminate()
        self.state.events["ShutdownEvent"].fire()

    @IRCCallback("INVITE")
    def invite(self, msg):
        chan = msg["arg"].split(":", 1)[1]
        bot._send("JOIN %s" % (chan))

    @IRCCallback("JOIN")
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
        msg = msg.strip('\r')
        msg = msg.strip(' ')
        lines = [self.style.merge_colors(self.defaultcolor, line) for line in msg.split('\n')]
        for i in lines:
            print("%r" % (i))
        msg = '\n'.join(lines)
        self._msg(chan, msg)

    @IRCCallback("353") # RPL_NAMREPLY
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
        channel.update_users(users)

    @IRCCallback("NOTICE")
    def notice(self, msg):
        """ Handle notices """
        actualargs = msg["arg"].split(" ", 1)[1][1:]
        sender = msg["host"].split("!")[0]
        self.state.notices.append({"sender": sender, "message": actualargs})
        self.state.events["NoticeEvent"].fire(self, sender, actualargs)

    @IRCCallback("NICK")
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

        if oldnick in self.state.users.keys() and oldnick != newnick:
            self.state.users[newnick] = self.state.users[oldnick]
            del self.state.users[oldnick]

    @IRCCallback("PART")
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

    @IRCCallback("PRIVMSG")
    def privmsg(self, msg):
        """ Handles messages. """
        # Split msg into parts

        if re.match("\x01(.+?)\x01", msg["arg"]):
            # ctcp
            self.handle_ctcp()
        nick = msg["host"].split("!")[0].lower()  # get sender
        nick_exact = msg["host"].split("!")[0]
        chan = msg["arg"].split()[0]  # get chan
        if not chan.startswith("#"):
            chan = nick  # if chan is a private message, file under them
            self.state.channels.add(chan)
            self.state.channels[chan].update_users({nick})
        chan = chan.lower()
        msg = msg["arg"].split(":", 1)[1]  # get msg

        self.state.events["MessageEvent"].fire(self, nick, chan, msg)

        if nick in self.state.muted and chan.startswith('#'):
            # In this case, we act like the message never happened
            # We ignore mute status in private message, as mute is usually
            # used to make the bot leave people alone.
            return

        self._check_for_command(msg, nick, chan)
        self._check_for_re_command(msg, nick, chan)

        msg = utils.message.Message(nick, self.state.channels[chan], msg)
        if nick in self.state.messages.keys():
            self.state.messages[nick].appendleft(msg)
        else:
            self.state.messages[nick] = deque([msg], MAX_MESSAGE_STORAGE)

        try:
            self.state.users[nick].exactnick = nick_exact
        except:
            traceback.print_exc()

    @IRCCallback("QUIT")
    def quit(self, msg):
        """ Handles quits. """
        nick = msg["host"].split("!")[0].lower()
        for channel in self.state.channels.get_channels_for(nick).values():
            channel.remove_user(nick)
        if self.state.users.get(nick, False):
            del self.state.users[nick]

    @IRCCallback("KICK")
    def kick(self, msg):
        """ Handles kicks. """
        nick = msg["arg"].split()[1].lower()
        chan = msg["arg"].split()[0].lower()
        channel = self.state.channels.get(chan, False)
        if channel:
            try:
                channel.remove_user(nick)
            except:
                traceback.print_exc()
        self.state.events["KickEvent"].fire(self, nick, chan)

    @IRCCallback("376", "422") # ENDOFMOTD or NOMOTD
    def welcome(self, *args):
        """ welcome(msg) - handles on-login actions """
        if self.config["ident_pass"]:
            self._msg(self.config["identify_service"], "identify %s"
                % (self.config["ident_pass"]))
        self._send("MODE %s +B" % (self.state.nick))
        self.state.events["WelcomeEvent"].fire(self)

if __name__ == "__main__":
    config = json.loads(open("config.json", "r").read())
    bot = James(config)
    bot.connect()

""" 
James.py - main bot
"""

from utils.irc import IRCHandler
import utils
import traceback
import re
import os
import sys
import yaml
import json
import plugins
from utils import logging
from utils.commandhandler import CommandHandler
from utils.decorators import startinfo, sethook

CONFIG = {}

class James(IRCHandler):
    """ James main bot executable thingy class """
    @startinfo('3.2.2')
    def __init__(self, config, verbose=False):
        super(James, self).__init__(config, verbose=verbose)
        globals()['CONFIG'] = config
        self.state = utils.ServerState()
        self.log = logging.Logger()
        self.data = {}
        self.data.update({'apikeys': yaml.safe_load(open('apikeys.conf'))})
        self.lastmsgof = {}
        self.cmdhandler = CommandHandler(self, plugins.get_plugins())

    def welcome(self, msg):
        """ welcome(msg) - handles on-login actions """
        self.msg(CONFIG['identify_service'], 'identify %s' % (CONFIG['ident_pass']))

    def names(self, msg):
        """ Executed on NAMES reply """
        chantype = re.match(r'(=|@|\*).*', msg['arg'].split(' ', 1)[1])
        chantype = chantype.groups()[0]
        args = msg['arg'].split(chantype)[1]
        channel = args.split(':')[0][:-1].strip()
        users = args.split(':')[1].split()
        modes = ['+', '%', '@', '&', '~']

        
        users = [u for u in users if not u[:1] in modes] + [u[1:] for u in users if u[:1] in modes]
        
        if not channel in self.state.get_channels():
            self.state.add_channel(channel, users)
        else:
            self.state.set_channel_users(channel, users)

    def topic(self, msg):
        """ Executed when someone changes the topic """
        channel = msg['arg'].split()[0]
        user = msg['host'].split('!')[0]
        topic = msg['arg'].split(' ', 1)[1][1:]
        self.state.set_channel_topic(channel, topic)
        self.log.log("%s set topic of %s to %s" % (user, channel, topic))

    def newtopic(self, msg):
        """ Executed when you join a new channel """
        args = msg['arg']
        topic = args.split(' ', 2)[2][1:]
        channel = args.split()[1].strip()
        if self.state.get_channel(channel):
            self.state.get_channel(channel)[0].set_topic(topic)
        else:
            self.state.add_channel(channel, '', topic=topic)

    def privmsg(self, msg):
        """ Handles Messages """
        nick = msg['host'].split('!')[0]
        chan = msg['arg'].split()[0]
        msg = msg['arg'].split(' ', 1)[1][1:]
        self.log.log(u"[%s] <%s> %s" % (chan, nick, msg))
        if msg.startswith('s/') and msg.count('/') == 3:
            if nick in self.lastmsgof.keys():
                sed_cmd = "echo \"%s\" | sed \"%s\""
                newmsg = os.popen(sed_cmd % (self.lastmsgof[nick], msg))
                newmsg = newmsg.read()
                self._msg(chan, "<%s> %s" % (nick, newmsg))
        self.lastmsgof[nick] = msg

        cmd_splitmsg = msg.split(" ", 1)

        triggered_short = self.cmdhandler.trigger_short(cmd_splitmsg[0])
        if triggered_short:
            try:
                if len(cmd_splitmsg) > 1:
                    cmd_args = cmd_splitmsg[1]
                else:
                    cmd_args = ''

                if hasattr(triggered_short.function, "_require_admin"):
                    if nick in self.state.admins:
                        triggered_short(self, nick, chan, cmd_args)
                else:
                    triggered_short(self, nick, chan, cmd_args)

            except BaseException:
                self._meditate(sys.exc_info(), chan)
                traceback.print_exc()

        self.check_for_command(msg, cmd_splitmsg, nick, chan)

    def check_for_command(self, msg, cmd_splitmsg, nick, chan):
        """ Check for a normal command starting with the command char. """
        if msg.startswith(CONFIG['cmdchar']):
            try:
                cmd_name = cmd_splitmsg[0][1:]
                if len(cmd_splitmsg) > 1:
                    cmd_args = cmd_splitmsg[1]
                else:
                    cmd_args = ''
                callback = self.cmdhandler.trigger(cmd_name)
                if not callback:
                    return self._msg(nick, "Unknown Command.")
                
                if hasattr(callback.function, '_require_admin'):
                    if nick in self.state.admins:
                        callback(self, nick, chan, cmd_args)
                else:
                    callback(self, nick, chan, cmd_args)
            except BaseException:
                self._meditate(sys.exc_info(), chan)
                traceback.print_exc()
                
    def _meditate(self, exc_info, chan):
        """ Prints GURU MEDITATION messages - at least, it used to. """
        exc_name = str(exc_info[0]).split("'")[1]
        exc_args = exc_info[1].args[0]
        if exc_args:
            self._msg(chan, \
                      "[\x02\x034GURU\x03 MEDITATION\x034 E:\x03 %s\x02] %s"\
                      % (exc_name, exc_args))
        else:
            self._msg(chan, \
                      "[\x02\x034GURU\x03 MEDITATION\x034 E:\x03 %s\x02]"\
                      % (exc_name))

    def nick(self, msg):
        """ Handles nickchanges """
        oldnick = msg['host'].split('!')[0]
        newnick = msg['arg'][1:]
        containers = self.state.get_channels_for_user(oldnick)
        if oldnick in self.state.admins:
            self.state.admins[self.state.admins.index(oldnick)] = newnick
        if containers:
            for container in containers:
                container.set_user(oldnick, newnick)

    def join(self, msg):
        """ Handles people joining channels """
        user = msg['host'].split('!')[0].strip()
        channel = msg['arg'][1:].strip()
        if user != CONFIG['nick']:
            self.state.get_channel(channel)[0].add_user(user)
        self.log.log("[%s] JOIN %s" % (channel, user))

    def part(self, msg):
        """ Handles people parting channels """
        channel = msg['arg'].split()[0].strip()
        user = msg['host'].split('!')[0].strip()
        try:
            self.state.get_channel(channel)[0].remove_user(user)
            self.log.log("[%s] PART %s" % (channel, user))
        except BaseException:
            traceback.print_exc()

    def _msg(self, chan, msg):
        """ _msg(string chan, string msg) - Sends a PRIVMSG. """
        if '\n' in msg:
            for item in msg.split('\n'):
                self._send("PRIVMSG %s :%s" % (chan, item))
        else:
            self._send("PRIVMSG %s :%s" % (chan, msg))

    def msg(self, chan, msg):
        """ msg(string chan, string msg) - Sends a PRIVMSG. """
        self._msg(chan, msg)

    def login(self, nick):
        """ login(string nick) - Login to the bot. """
        self.state.add_admin(nick)

    def gracefully_terminate(self):
        """ Handles the quit routine, then exits. """
        try:
            super(James, self).gracefully_terminate()
        except SystemExit:
            pass
        self.log.close()


if __name__ == '__main__':
    ARGS = sys.argv[1:]
    print(ARGS)
    CONFIG = json.loads(open('config.json', 'r').readline())
    if '--verbose' in ARGS:
        BOT = James(CONFIG, verbose=True)
    else:
        BOT = James(CONFIG)
    BOT.connect()

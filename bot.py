""" 
James.py - main bot
"""

from straight.plugin import load
from utils.irc import IRCHandler
import utils
import traceback
import re
import random
import sys
import os
import yaml
from utils import logging

config = {}

class James(IRCHandler):
    """ James main bot executable thingy class """
    def __init__(self, config):
        super(James, self).__init__(config)
        globals()['config'] = config
        self.cmdhandler = utils.commandhandler.CommandHandler(load('plugins'))
        self.state = utils.ServerState()
        self.log = logging.Logger()
        self.data = {}
        self.data.update({'apikeys': yaml.safe_load(open('apikeys.conf'))})
        self.lastmsgof = {}

    def names(self, msg):
        chantype = re.match('(=|@|\*).*', msg['arg'].split(' ', 1)[1]).groups()[0]
        args = msg['arg'].split(chantype)[1]
        channel = args.split(':')[0][:-1].strip()
        users = args.split(':')[1].split()
        modes = ['+', '%', '@', '&', '~']

        
        users_without_status = [u for u in users if not u[:1] in modes]
        users = users_without_status + [u[1:] for u in users if u[:1] in modes]
        
        if not channel in self.state.get_channels():
            self.state.add_channel(channel, users)
        else:
            self.state.set_channel_users(channel, users)

    def topic(self, msg):
        channel = msg['arg'].split()[0]
        user = msg['host'].split('!')[0]
        topic = msg['arg'].split(' ', 1)[1][1:]
        self.state.set_channel_topic(channel, topic)
        self.log.log("%s set topic of %s to %s" % (user, channel, topic))

    def newtopic(self, msg):
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
        self.log.log("[%s] <%s> %s" % (chan, nick, msg))
        if msg.startswith('s/') and msg.count('/') == 3 and nick in self.lastmsgof.iterkeys():
            newmsg = os.popen("echo \"%s\" | sed \"%s\"" % (self.lastmsgof[nick], msg)).read()
            self._msg(chan, "<%s> %s" % (nick, newmsg))
        self.lastmsgof[nick] = msg
            
        if msg.startswith(config['cmdchar']):
            try:
                cmd_splitmsg = msg.split(" ", 1)
                cmd_name = cmd_splitmsg[0][1:]
                if len(cmd_splitmsg) > 1:
                    cmd_args = cmd_splitmsg[1]
                else:
                    cmd_args = ''
                callback = self.cmdhandler.trigger(cmd_name)
                if not callback:
                    self._msg(nick, "Unknown Command.")
                elif not hasattr(callback, '_requireadmin'):
                    callback(self, nick, chan, cmd_args)
                else:
                    if nick in self.state.admins:
                        callback(self, nick, chan, cmd_args)
            except:
                self._meditate(sys.exc_info(), chan)
                traceback.print_exc()
                
    def _meditate(self, exc_info, chan):
        exc_name = str(exc_info[0]).split("'")[1].split(".")[1]
        exc_args = exc_info[1].message
        if exc_args:
            self._msg(chan, "[\x02\x034GURU\x03 MEDITATION\x034 ERROR\x03 %s\x02] %s"\
                      % (exc_name, exc_args))
        else:
            self._msg(chan, "[\x02\x034GURU\x03 MEDITATION \x034 ERROR\x03 %s\x02]"\
                      % (exc_name))

    def nick(self, msg):
        oldnick = msg['host'].split('!')[0]
        newnick = msg['arg'][1:]
        containers = self.state.get_channels_for_user(oldnick)
        if oldnick in self.state.admins:
            self.state.admins[self.state.admins.index(oldnick)] = newnick
        if containers:
            for container in containers:
                container.set_user(oldnick, newnick)

    def join(self, msg):
        user = msg['host'].split('!')[0].strip()
        channel = msg['arg'][1:].strip()
        if user != config['nick']:
            self.state.get_channel(channel)[0].add_user(user)
        self.log.log("%s joined %s." % (user, channel))

    def part(self, msg):
        channel = msg['arg'].split()[0].strip()
        user = msg['host'].split('!')[0].strip()
        try:
            self.state.get_channel(channel)[0].remove_user(user)
            self.log.log("%s left %s." % (user, channel))
        except:
            traceback.print_exc()

    def _msg(self, chan, msg):
        self._send(u"PRIVMSG %s :%s" % (chan, msg))

    def login(self, nick):
        self.state.add_admin(nick)

    def gracefully_terminate(self):
        try:
            super(James, self).gracefully_terminate()
        except SystemExit:
            pass
        self.log.close()


if __name__ == '__main__':
    CONFIG = {'server': 'irc.awfulnet.org:6667', 'nick':\
              'James3', 'real': "James3 - the most amazing bot on the net", \
              'user': 'james', 'plugdir': 'plugins', 'joinchans':\
              ['#teenagers'], 'cmdchar': '+'}
    BOT = James(CONFIG)
    BOT.connect()

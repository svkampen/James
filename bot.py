""" 
James.py - main bot
"""

from straight.plugin import load
from utils.irc import IRCHandler
import utils
import traceback

config = {}

class James(IRCHandler):
    """ James main bot executable thingy class """
    def __init__(self, config):
        super(James, self).__init__(config)
        globals()['config'] = config
        self.cmdhandler = utils.commandhandler.CommandHandler(load('plugins'))
        self.state = utils.ServerState()

    def names(self, msg):
        args = msg['arg'].split('=')[1]
        channel = args.split(':')[0][:-1]
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
        topic = msg['arg'].split(' ', 1)[1][1:]
        self.state.set_channel_topic(channel, topic)

    def newtopic(self, msg):
        args = msg['arg']
        print("I am being called!")
        topic = args.split(' ', 2)[2][1:]
        channel = args.split()[1]
        print('%s %s'  % (channel, topic))
        self.state.add_channel(channel, [''], topic=topic)

    def privmsg(self, msg):
        """ Handles Messages """
        nick = msg['host'].split('!')[0]
        chan = msg['arg'].split()[0]
        msg = msg['arg'].split(' ', 1)[1][1:]
        print("[%s] <%s> %s" % (chan, nick, msg))
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
                traceback.print_exc()

    def nick(self, msg):
        oldnick = msg['host'].split('!')[0]
        newnick = msg['arg'][1:]
        if oldnick in self.state.admins:
            self.admins[self.admins.index(oldnick)] = newnick

    def _msg(self, chan, msg):
        self._send("PRIVMSG %s :%s" % (chan, msg))

    def login(self, nick):
        self.state.add_admin(nick)


if __name__ == '__main__':
    CONFIG = {'server': 'irc.awfulnet.org:6667', 'nick':\
              'James3', 'real': "James3 - the most amazing bot on the net", \
              'user': 'james', 'plugdir': 'plugins', 'joinchans':\
              ['#teenagers'], 'cmdchar': '+'}
    BOT = James(CONFIG)
    BOT.connect()

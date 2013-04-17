""" 
James.py - main bot
"""

import irc

if __name__ == '__main__':
    CONFIG = {'server': 'irc.awfulnet.org:6667', 'nick':\
              'James3', 'real': "James3 - the most amazing bot on the net", \
              'user': 'james', 'plugdir': 'plugins', 'joinchans':\
              ['#teenagers'], 'cmdchar': '+'}
    BOT = irc.IRC(CONFIG)

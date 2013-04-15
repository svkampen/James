""" 
IRC Parser - parse.py
"""

def parse(msg):
    if msg.startswith("PING"):
        info = {'method': 'PING', 'arg': msg.split()[-1]}
    else:
        splitmsg = msg.split(' ', 2)
        info = {'method': splitmsg[1], 'host': splitmsg[0][1:], 'arg':\
                splitmsg[2]}
    return info

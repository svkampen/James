#!/usr/bin/python
#
#

import json
import os
from pprint import pformat as pprint

json_dict = dict()
config_file = open("config.json", "w+")

try:
    input = raw_input
    #py2
except NameError:
    pass # py3k

print("Starting makeconfig version 1.0")

json_dict['server'] = input("Server: ")
json_dict['port'] = input("Port (default=6667): ")
if not json_dict['port']:
    json_dict['port'] = 6667

json_dict['pass'] = input("Server password (default=none): ")
if not json_dict['pass']:
    json_dict['server'] = "%s:%s" % (json_dict['server'], json_dict['port'])
else:
    json_dict['server'] = "%s:%s|%s" % (json_dict['server'], json_dict['port'], json_dict['pass'])

json_dict['nick'] = input("Username (default=James): ")
if not json_dict['nick']:
    json_dict['nick'] = 'James'

json_dict['real'] = 'James - the most amazing bot on the net'
json_dict['user'] = 'james'
json_dict['admins'] = [input("Initial admin username: ")]

json_dict['cmdchar'] = input("Command character (default='+'): ")
if not json_dict['cmdchar']:
    json_dict['cmdchar'] = '+'

json_dict['identify_service'] = input("Service to identify with (default=NickServ): ")
if not json_dict['identify_service']:
    json_dict['identify_service'] = 'NickServ'

json_dict['ident_pass'] = input("Password to identify with: ")
json_dict['autojoin'] = []

for item in input("Channels to automatically join, seperated by ',': ").split(','):
    json_dict['autojoin'].append(item)

json_dict.pop('port')

config_file.write(pprint(json_dict).replace("'", '"'))
config_file.close()

if not os.path.exists('apikeys.conf'):
    # populate the apikeys file with nothing
    apikeys_file = open('apikeys.conf', 'w')
    apikeys_file.write('{}')
    apikeys_file.close()

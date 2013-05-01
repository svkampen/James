#!/usr/bin/python
#
#

import json

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

json_dict['server'] = "%s:%d" % (json_dict['server'], json_dict['port'])

json_dict['nick'] = input("Username (default=James3): ")
if not json_dict['nick']:
    json_dict['nick'] = 'James3'

json_dict['real'] = 'James3 - the most amazing bot on the net'
json_dict['user'] = 'james'
json_dict['plugdir'] = input("Plugin dir (default=plugins): ")
if not json_dict['plugdir']:
    json_dict['plugdir'] = 'plugins'

json_dict['cmdchar'] = input("Command character (default='+'): ")
if not json_dict['cmdchar']:
    json_dict['cmdchar'] = '+'

json_dict['identify_service'] = input("Service to identify with (default=NickServ): ")
if not json_dict['identify_service']:
    json_dict['identify_service'] = 'NickServ'

json_dict['ident_pass'] = input("Password to identify with: ")

json_dict.pop('port')

json_ = json.dumps(json_dict)
config_file.write(json_)
config_file.close()

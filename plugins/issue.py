""" 
Integration with the James issue tracker.
"""
from .util.decorators import command, initializer
import requests
import json

@command('request.feature', 'reqfeature')
def request_feature(bot, nick, chan, arg):
    ''' Request a feature on the James issue tracker. '''
    print('test')
    if not arg:
        return bot._msg(chan, "Usage: requestfeat title: description")

    arg = arg.split(": ")
    # arg[0] = title, arg[1] = description.

    github_url = 'https://api.github.com/repos/svkampen/James/issues'
    auth_data = bot.data['apikeys']['github']
    auth = (auth_data['user'], auth_data['pass'])
    headers = {'Content-Type': 'application/json'}
    payload = {'title': arg[0], 'body': arg[1], 'assignee': 'svkampen', \
               'labels': ['want']}
    data = json.dumps(payload)

    page = requests.post(github_url, data=data, auth=auth, headers=headers)
    data = page.json()
    if page.status_code == 201:
        bot._msg(chan, "Posted request on issue tracker. URL: %s"\
                 % (bot.data['shortener'](bot, data['html_url'])))
    else:
        bot._msg(chan, "Eh.. there was some sort of error. Status code: %d"
                 % (page.status_code))

@command('report.bug')
def report_bug(bot, nick, chan, arg):
    """ Report a bug on the James issue tracker. """
    if not arg:
        return bot._msg(chan, "Usage: report.bug title: description")

    arg = arg.split(": ")
    github_url = 'http://api.github.com/repos/svkampen/James/issues'
    auth_data = bot.data['apikeys']['github']
    auth = (auth_data['user'], auth_data['pass'])
    headers = {'Content-Type': 'application/json'}
    payload = {'title': arg[0], 'body': arg[1], 'assignee': 'svkampen', \
               'labels': ['bug']}
    data = json.dumps(payload)

    page = requests.post(github_url, data=data, auth=auth, headers=headers)
    data = page.json()
    if page.status_code == 201:
        bot._msg(chan, "Posted bug report. URL: %s"\
                 % (bot.data['shortener'](bot, data['html_url'])))

@initializer
def initialize_plugin(bot):
    """ Initialize this plugin. """
    pass
#    if not 'github' in bot.data['apikeys'].keys():
#        del globals()['request_feature']
#        del globals()['report_bug']
#    if not 'shortener' in bot.data.keys():
#        del globals()['request_feature']
#        del globals()['report_bug']
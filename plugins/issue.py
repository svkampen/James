"""
Integration with the James issue tracker.
"""
from .util.decorators import command, initializer
import requests
import json
from .util.data import www_headers as headers, get_doc

def get_auth(bot):
    ghub = bot.state.apikeys["github"]
    return (ghub["user"], ghub["pass"])

@command("request.feature", "reqfeature", category="git")
def request_feature(bot, nick, chan, arg):
    """ request.feature <title>: <desc> -> Request a feature. """
    if not arg:
        return bot._msg(chan, get_doc())

    if (":" in arg):
        arg = arg.split(": ")
    else:
        arg = [arg, ""]
    # arg[0] = title, arg[1] = description.

    github_url = "https://api.github.com/repos/svkampen/James/issues"
    auth_data = bot.state.apikeys.get("github", {"user": False, "pass": False})
    auth = (auth_data["user"], auth_data["pass"])
    headers = {"Content-Type": "application/json"}
    payload = {"title": arg[0], "body": arg[1], "assignee": "svkampen",
               "labels": ["want"]}
    data = json.dumps(payload)

    page = requests.post(github_url, data=data, auth=auth, headers=headers)
    data = page.json()
    if page.status_code == 201:
        bot._msg(chan, "\x0314\x0313%s \x0314#%s \x0314\x0302 ⟶ \x0314%s"
                 % (arg[0], data["number"], bot.state.data["shortener"](bot,
                    data["html_url"])))
    else:
        bot._msg(chan, "Eh.. there was some sort of error. Status code: %d"
                 % (page.status_code))


@command("report.bug", category="git")
def report_bug(bot, nick, chan, arg):
    """ report.bug <title>: <desc> -> Report a bug. """
    if not arg:
        return bot._msg(chan, get_doc())

    if (":" in arg):
        arg = arg.split(": ")
    else:
        arg = [arg, ""]
    github_url = "https://api.github.com/repos/svkampen/James/issues"
    auth_data = bot.state.apikeys.get("github", {"user": False, "pass": False})
    auth = (auth_data["user"], auth_data["pass"])
    headers = {"Content-Type": "application/json"}
    payload = {"title": arg[0], "body": arg[1], "assignee": "svkampen",
               "labels": ["bug"]}
    data = json.dumps(payload)

    page = requests.post(github_url, data=data, auth=auth, headers=headers)
    print(page.text)
    data = page.json()
    if page.status_code == 201:
        bot._msg(chan, "\x0314\x0313%s \x0314#%s \x0314\x0302 ⟶ \x0314%s"
                 % (arg[0], data["number"], bot.state.data["shortener"](bot,
                    data["html_url"])))
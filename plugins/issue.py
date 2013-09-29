"""
Integration with the James issue tracker.
"""
from .util.decorators import command, initializer
import requests
import json
from .github import get_auth
from .util.data import www_headers as headers

@command("github.get_issues", category="git")
def get_github_issues(bot, nick, chan, arg):
    """ github.get_issues -> get all issues on James' issue tracker """
    req = requests.get("https://api.github.com/repos/svkampen/James/issues",
        headers=headers, auth=get_auth(bot))
    data = req.json()
    for issue in data:
        num = issue["number"]
        content = "%s: %s" % (issue["title"], issue["body"])
        bot.msg(chan, "[%s] %s" % (num, content))


@command("github.get_issue", category="git")
def get_github_issue(bot, nick, chan, arg):
    """ github.get_issue #<n> -> get github issue #<n> """
    args = arg.split()
    if len(args) == 2:
        repo = args[0]
        num = args[1]
    else:
        repo = "svkampen/James"
        num = arg[1:]
    req = requests.get("https://api.github.com/repos/%s/issues/%s" % (repo, num),
        headers=headers, auth=get_auth(bot))
    if not req.status_code == 200:
        return bot.msg(chan, "An error occurred fetching the issue. Status code: %s"
            % (req.status_code))

    data = req.json()
    
    title = data["title"]
    body = data["body"]

    bot.msg(chan, "#%s - %s: %s" % (num, title, body))

@command("github.close_issue", category="git")
def close_github_issue(bot, nick, chan, arg):
    """ github.close_issue #<num> -> close an issue on github """
    try: 
        int(arg[1:])
    except ValueError:
        return bot.msg(chan, close_github_issue.__doc__.strip())
    payload = '{"state": "closed"}'
    num = arg[1:]
    url = "https://api.github.com/repos/svkampen/James/issues/%s" % (num)
    req = requests.patch(url, headers=headers, data=payload, auth=get_auth(bot))
    data = req.json()
    bot.msg(chan, "Closed issue %s (%s)" % (arg, data["html_url"]))


@command("request.feature", "reqfeature", category="git")
def request_feature(bot, nick, chan, arg):
    """ request.feature <title>: <desc> -> Request a feature. """
    if not arg:
        return bot._msg(chan, "Usage: requestfeat title: description")

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
        bot._msg(chan, "Posted request #%s. URL: %s"
                 % (data["number"], bot.state.data["shortener"](bot,
                    data["html_url"])))
    else:
        bot._msg(chan, "Eh.. there was some sort of error. Status code: %d"
                 % (page.status_code))


@command("report.bug", category="git")
def report_bug(bot, nick, chan, arg):
    """ report.bug <title>: <desc> -> Report a bug. """
    if not arg:
        return bot._msg(chan, "Usage: report.bug title: description")

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
        bot._msg(chan, "Posted bug report #%s URL: %s"
                 % (data["number"], bot.state.data["shortener"](bot,
                    data["html_url"])))


@initializer
def initialize_plugin(bot):
    """ Initialize this plugin. """
    pass
#    if not "github" in bot.state.data["apikeys"].keys():
#        del globals()["request_feature"]
#        del globals()["report_bug"]
#    if not "shortener" in bot.state.data.keys():
#        del globals()["request_feature"]
#        del globals()["report_bug"]

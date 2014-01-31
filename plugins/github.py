"""
General Githubbery
"""

from .util.decorators import command
from .util.data import www_headers as headers, lineify, get_doc
import requests
import time


def getpercentage(part, whole):
    return 100 * float(part)/float(whole)

def get_auth(bot):
    return (bot.state.apikeys["github"]["user"], bot.state.apikeys["github"]["pass"])

@command("github.what.is", category="git")
def what(bot, nick, chan, arg):
    """ github.what.is <user/repo> -> Get the description of a github repository """
    if not arg:
        return bot.msg(chan, get_doc())
    response = requests.get("https://api.github.com/repos/%s" % (arg),
        headers=headers, auth=get_auth(bot))
    if response.status_code == 200:
        return bot.msg(chan, "\x02%s\x02 -- %s" % (response.json()["full_name"],
            response.json()["description"]))
    else:
        return bot.msg(chan, "\x02Unknown repository\x02 %s" % (arg))


@command("github.stats_for", category="git")
def repostats(bot, nick, chan, arg):
    """ github.stats_for <user/repo> -> Get statistics for a github repository """
    if not arg:
        return bot.msg(chan, get_doc())
    c_response = requests.get("https://api.github.com/repos/%s/stats/contributors" % (arg),
        headers=headers, auth=get_auth(bot))
    if c_response.status_code in (200, 202):
        json = c_response.json()
        commits = [i["total"] for i in json]
        commits = sum(commits)
    else:
        commits = -1
    time.sleep(0.1)
    l_response = requests.get("https://api.github.com/repos/%s/languages" % (arg),
        headers=headers, auth=get_auth(bot))
    if l_response.status_code in (200, 202):
        json = l_response.json()
        whole = sum(json.values())
        langs_percents = {k: getpercentage(v, whole) for k, v in json.items()}
    else:
        langs_percents = {"unknownlang": 100.0}
    time.sleep(0.1)
    r_response = requests.get("https://api.github.com/repos/%s" % (arg), headers=headers, auth=get_auth(bot))
    if r_response.status_code in (200, 202):
        json = r_response.json()
        forks = json["forks"]
        open_issues = json["open_issues"]
        watchers = json["watchers"]
        master_branch = json["master_branch"]
    else:
        forks = 0
        open_issues = 0
        watchers = 0
        master_branch = "master"

    #langs_percents = {k:v for k,v in zip(langs_percents.keys(), sorted(langs_percents.values())[::-1])}
    langout = ["%s (%s%%)" % (k, v) for k, v in langs_percents.items()]
    output = "Statistics for: \x02%s\x02\n" % (arg)
    output += "Commit count: %s -  Master Branch: %s\nLanguages: " % (str(commits), master_branch)
    langout = ", ".join(langout)
    langout = lineify(langout)
    output += "\n".join(langout)
    output += "\nForks: %d - Open Issues: %d - Watchers: %d\n" % (forks, open_issues, watchers)
    return bot.msg(chan, output)

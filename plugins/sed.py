from .util.decorators import command, initializer, require_admin
import itertools
import re
import codecs
import traceback
from itertools import zip_longest
import string

string.ascii = [chr(i) for i in range(128)]

SUB_REGEX = re.compile(r"^(?:(\S+)[:,]\s)?(?:s|(.+?)/s)/((?:\\/|[^/])+)\/((?:\\/|[^/])*?)/([gixs]{0,4})?")
TRANS_REGEX = re.compile(r"^(?:(\S+)[:,]\s)?(?:y|(.+?)/y)/((?:\\/|[^/])+)\/((?:\\/|[^/])*?)/([cds]+)?")

@command('topicsed', category="meta")
def sed_topic(bot, nick, chan, args):
    s = Substitution(args)
    sub = s.do(bot.state.channels[chan].topic)
    bot.set_topic(chan, sub)

def sed(bot, nick, chan, msg):
    if not SUB_REGEX.match(msg) and not TRANS_REGEX.match(msg):
        return # this isn't a sed message

    if SUB_REGEX.match(msg):
        do_sub(bot, nick, chan, msg)
    elif TRANS_REGEX.match(msg):
        tr(bot, nick, chan, msg)


def squeeze(lst, src):
    for ch in lst:
        src = re.sub(ch + r"{2,}", ch, src)
    return src

def sugar(src):
    return src.replace("\\/", "/") \
            .replace("[:upper:]", string.ascii_uppercase) \
            .replace("[:lower:]", string.ascii_lowercase) \
            .replace("[:alpha:]", string.ascii_letters) \
            .replace("[:digit:]", string.digits) \
            .replace("[:xdigit:]", string.hexdigits) \
            .replace("[:alnum:]", string.digits + string.ascii_letters) \
            .replace("[:blank:]", string.whitespace) \
            .replace("[:punct:]", string.punctuation) \
            .replace("[:cntrl:]", "".join([i for i in string.ascii if not i in string.printable])) \
            .replace("[:print:]", string.printable)

def expand(src):
    out = []
    escaped = False
    hyphen = False

    for char in src:
        if char == "\\":
            escaped = True
            continue
        elif char == '-' and not escaped:
            hyphen = True
            escaped = False
            continue
        elif hyphen:
            out.extend(range(out[-1] + 1, ord(char)))
            hyphen = False
        out.append(ord(char))
    return "".join([chr(i) for i in out])


def tr(bot, nick, chan, msg):
    target, qual, lhs, rhs, flags = TRANS_REGEX.match(msg).groups()


    # if there is no qualifier, match the last message from this chan using .+
    target = target or nick

    lhs = expand(sugar(lhs))
    rhs = expand(sugar(rhs))

    qual = qual or '|'.join(list(lhs))

    trans_table = {ord(i[0]):i[1] for i in itertools.zip_longest(lhs, rhs, fillvalue=rhs[-1])}

    msg = get_tr_message(bot, qual, target.lower(), chan)

    msg = msg.translate(trans_table)
    if '\x01' in msg:
        msg = msg.split(" ", 1)[1][:-1]
        return bot.msg(chan, "* %s %s" % (target, msg))
    return bot.msg(chan, "<%s> %s" % (target, msg))



class Substitution(object):
    """ A class representing a substitution in sed. """
    def __init__(self, pattern):
        self.pattern = pattern
        self.target, self.qual, self.re, self.sub, self.flags, self.count = self.parse(pattern)

    def __repr__(self):
        return "Substitution(%r)" % (self.pattern)

    def parse(self, pattern):
        m = SUB_REGEX.match(pattern)
        if not m:
            raise TypeError("Pattern %r isn't a proper substitution pattern!" % (pattern))
        count = 1

        groups = m.groups()
        if 'g' in groups[4]:
            count = 0

        flags = 0
        for c in groups[4]: # for character in flags
            if c != 'g':
                flags += getattr(re, c.upper())

        sub = groups[3].replace("\\/", "/")
        sub = re.sub(r"(?<!\\)(\\)(?=\d+|g<\w+>)", r"\\\\", sub)
        sub = codecs.escape_decode(bytes(sub, "utf-8"))[0].decode('utf-8')

        return list(groups[:-2]) + [sub, flags, count]

    def do(self, on):
        return re.sub(self.re, self.sub, on, count=self.count, flags=self.flags)


def do_sub(bot, nick, chan, msg):
    if not (bot.getconfig()["sed-enabled"]):
        return
    sub = Substitution(msg)

    if sub.target:
        nick = sub.target

    nick = bot.state.users[nick.lower()].exactnick

    message = get_sub_message(bot, sub, nick.lower(), chan)

    if not message:
        print(nick.lower(), str(sub))
        return

    new_msg = sub.do(message.msg)

    if '\n' in new_msg:
        bot.msg(chan, "you guys are all assholes")
        return

    if message.is_action:
        return bot.msg(chan, "* %s %s" % (nick, new_msg))

    return bot.msg(chan, "<%s> %s" % (nick, new_msg))

def get_tr_message(bot, qual, nick, chan):
    if not nick in bot.state.messages:
        return ""

    for message in bot.state.messages[nick]:
        if message.channel != bot.state.channels[chan]:
            continue
        if re.search(qual, message.msg):
            return message.msg
    return ""

def get_sub_message(bot, sub, nick, chan):
    target = nick

    if not target in bot.state.messages:
        return ""

    for message in bot.state.messages[nick]:
        if not message.channel == bot.state.channels[chan]:
            continue
        msg = message.msg
        try:
            if sub.qual:
                if re.search(sub.re, msg) and re.search(sub.qual, msg) and not SUB_REGEX.match(msg):
                    return message
            else:
                if re.search(sub.re, msg) and not SUB_REGEX.match(msg):
                    return message
        except BaseException:
            traceback.print_exc()
    return ""

@initializer
def pluginit(bot):
    if bot.config["sed-enabled"]:
        bot.state.events.MessageEvent.register(sed)

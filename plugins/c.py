import os
from .util.decorators import command, require_admin

@require_admin
@command("c", category="misc")
def c_run(bot, nick, chan, arg):
    t = open("tmp.c", "w")
    t.write("#include <stdlib.h>\n#include <stdio.h>\n#include <string.h>\n#include <stdint.h>\n")
    t.write(arg)
    t.close()
    os.system("gcc -std=gnu99 -o tmp tmp.c")
    bot.msg(chan, os.popen("bash -c './tmp'").read())

"""
Threads module
"""

from threading import Thread
from queue import Queue
import traceback
import sys

class HandlerThread(Thread):
    def __init__(self, bot):
        self.bot = bot
        self.queue = Queue()
        super().__init__()

    def guru_meditate(self, chan, exc_info):
        exc_name = str(exc_info[0]).split("'")[1]
        exc_args = exc_info[1].args[0]
        exc_traceback = exc_info[2]
        outp = traceback.format_tb(exc_traceback)
        lineno = outp[-1].split(', ')[1][5:]
        file = ' '.join(outp[-1].split('"')[1].rsplit("/", 2)[-2:])
        out = "⌜ \x02\x03such \x034%s \x03so \x034%s\x03\x02 in \x034%s\x03 \x02line\x0304 %s\x03\x02 ⌟" % (
            exc_name, exc_args, file, lineno)
        self.bot.msg(chan, out)

    def run(self):
        while True:
            try:
                func = self.queue.get()
                func_chan = func.args[2]
                func()
            except BaseException as e:
                if not isinstance(e, SystemExit):
                    traceback.print_exc()
                    self.guru_meditate(func_chan, sys.exc_info())

    def handle(self, function):
        self.queue.put(function)


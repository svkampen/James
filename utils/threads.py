"""
Threads module
"""

from threading import Thread
from queue import Queue
import traceback

class HandlerThread(Thread):
    def __init__(self):
        self.queue = Queue()
        super().__init__()

    def run(self):
        while True:
            try:
                func = self.queue.get()
                func.call()
            except BaseException as e:
                if not isinstance(e, SystemExit):
                    traceback.print_exc()

    def handle(self, function):
        self.queue.put(function)


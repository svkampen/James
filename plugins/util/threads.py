from threading import Thread
import requests
import time
from .data import www_headers as headers

class Ticker(Thread):
    def __init__(self, url, sleeptime=30, hooks=None):
        super().__init__()
        if not hooks: hooks = []
        self.sleep_time = sleeptime
        self.url_to_query = url
        self.hooks = hooks
        self.running = True

    def run(self):
        """ Very basic Ticker thread. """
        self.loops=0
        while self.running:
            if self.loops == 0: time.sleep(1)
            else:
                time.sleep(self.sleep_time)
            self.response = requests.get(self.url_to_query, headers=headers)
            response = self.response
            for function in self.hooks:
                function(response)
            self.loops = 1

            

"""
Threads module
"""

from threading import Thread
from queue import Queue

class HandlerThread(Thread):
	def __init__(self):
		self.queue = Queue()
		super().__init__()

	def run(self):
		while True:
			func = self.queue.get()
			func.call()

	def handle(self, function):
		self.queue.put(function)


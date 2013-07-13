"""
Logging module
"""

from .util.decorators import initializer

def log_message(*args):
	...

def log_join(*args):
	...

def log_part(*args):
	...

def log_welcome(*args):
	...

def logger(*args, **kwargs):
	etype = kwargs['type']
	handlers = {'message': log_message,
	 'join': log_join,
	 'part': log_part,
	 'welcome': log_welcome}
    handlers.get(etype, lambda *args: None)(*args)

@initializer
def plugin_init(bot):
	for event in bot.state.events:
		event.register(logger)
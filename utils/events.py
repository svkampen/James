StandardEvents = [
    'WelcomeEvent',
    'JoinEvent',
    'PartEvent',
    'MessageEvent'
]

class Event():
    def __init__(self):
        self.handlers = set()

    def register(self, handler):
        self.handlers.add(handler)
        return self

    def fire(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise EventError("Can't unhandle handler %s: handler %s does not hook into this event!" % (handler, handler))

class EventError(BaseException):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

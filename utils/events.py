import traceback

Standard = [
    {'WelcomeEvent': 'welcome'},
    {'JoinEvent': 'join'},
    {'PartEvent': 'part'},
    {'MessageEvent': 'message'},
    {'NoticeEvent': 'notice'}
]


class Event():
    """ A simple event class """
    def __init__(self, type_):
        self.handlers = set()
        self.type = type_

    def register(self, handler):
        """ Register a function as an event handler """
        self.handlers.add(handler)
        return self

    def fire(self, *args, **kwargs):
        """ Fire this event """
        kwargs.update({'type': self.type})
        try:
            for handler in self.handlers:
                handler(*args, **kwargs)
        except:
            traceback.print_exc()

    def unhandle(self, handler):
        """ De-register an event handler from this event. Throws EventError"""
        try:
            self.handlers.remove(handler)
        except:
            raise EventError("Can't unhandle handler %s: \
                handler %s does not hook into this event!" % (handler, handler))


class EventError(BaseException):
    """ EventError class - When something goes wrong in an event."""
    def __init__(self, value):
        super().__init__(value)
        self.value = value

    def __str__(self):
        return self.value

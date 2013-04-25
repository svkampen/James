import os, sys
__all__ = [ file.split('.')[0] for file in os.listdir('./plugins') if file.endswith('.py')]
[__import__(__name__, fromlist=[item]) for item in __all__]
current_module = sys.modules[__name__]

def get_plugins():
    _plugins = []
    for key, attribute in current_module.__dict__.items():
        if not key.startswith("_"):
            _plugins.append(attribute)
    return _plugins

del os
del sys

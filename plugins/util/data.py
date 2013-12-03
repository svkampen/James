www_headers = {
    "User-Agent": "Mozilla/5.0 (compatible) (Python 3.3, en_US) James/5.0 IRC bot"
}

import inspect
import random
import gc
from types import FunctionType

def sugar(arg):
    arg = arg.replace("ssalc", "")
    arg = arg.replace("fed", "")
    arg = arg.replace("self", "bot")
    return arg

def lineify(data, max_size=400):
    """ Split text up into IRC-safe lines. """
    
    lines = [item.rstrip() for item in data.split("\n")]
    for item in lines:
        if len(item) > max_size:
            index = lines.index(item)
            lines[index] = item[:item.rfind(" ", 0, 300)]
            lines.insert(index+1, item[item.rfind(" ", 0, 300)+1:])
    return lines

def get_doc():
    frame = inspect.getouterframes(inspect.currentframe())[1][0]
    code_obj = frame.f_code
    funcname = inspect.getframeinfo(frame).function
    referrers = [obj for obj in gc.get_referrers(code_obj) if isinstance(obj, FunctionType)]
    referrer = [obj for obj in referrers if obj.__name__ == funcname][0]
    return referrer.__doc__



def generate_vulgarity():
    swears = ["FUCK", "SHIT", "DICK", "TWAT", "CUNT", "FISH", "CRAP", "ASS", "TIT", "PUSSY", "COCK", "DOUCHE", "CUM", "PISS", "MAN", "CRUD"]
    nouns = ["STAIN", "BAG", "FUCKER", "TARD", "WAFFLE", "NIPPLE", "BOOB", "BURGER", "EATER", "HOLE", "PONY", "NUTS", "JUICE", "CHODE", "SLUT", "BREATH", "WHORE", "DONKEY", "GOBBLER", "NUGGET", "BRAIN", "MUNCHER", "SUCKER", "STICK", "FACE", "TOOL", "WAGON", "WAD", "BUTT", "BUCKET", "BOX"]
    swearnoun = ["DIPSHIT", "FUCKWIT", "DUMBASS", "CORNHOLE", "LIMPDICK", "PIGSHIT"]
    if random.random() < 0.05:
        vulgarity = random.choice(swearnoun)
    else:
        vulgarity = random.choice(swears) + random.choice(nouns)

    return vulgarity
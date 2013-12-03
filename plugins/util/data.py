www_headers = {
    "User-Agent": "Mozilla/5.0 (compatible) (Python 3.3, en_US) James/5.0 IRC bot"
}

import inspect
import random

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

def get_caller_local(stack, local):
    return stack[1][0].f_locals.get(local, None)

def get_doc():
    stack = inspect.getouterframes(inspect.currentframe())[1:]
    return get_caller_local(stack, "callee_doc").strip()

def generate_vulgarity():
    swears = ["FUCK", "SHIT", "DICK", "TWAT", "CUNT", "FISH", "CRAP", "ASS", "TIT", "PUSSY", "COCK", "DOUCHE", "CUM", "PISS", "MAN", "CRUD"]
    nouns = ["STAIN", "BAG", "FUCKER", "TARD", "WAFFLE", "NIPPLE", "BOOB", "BURGER", "EATER", "HOLE", "PONY", "NUTS", "JUICE", "CHODE", "SLUT", "BREATH", "WHORE", "DONKEY", "GOBBLER", "NUGGET", "BRAIN", "MUNCHER", "SUCKER", "STICK", "FACE", "TOOL", "WAGON", "WAD", "BUTT", "BUCKET", "BOX"]
    swearnoun = ["DIPSHIT", "FUCKWIT", "DUMBASS", "CORNHOLE", "LIMPDICK", "PIGSHIT"]
    if random.random() < 0.05:
        vulgarity = random.choice(swearnoun)
    else:
        vulgarity = random.choice(swears) + random.choice(nouns)

    return vulgarity
import math

box = {'lbot': '└', 'vert': '│', 'rbot': '┘', 'ltop': '┌', 'tsplit': '┬',
       'horz': '─', 'rtsplit': '┴', 'rtop': '┐'}

def divide(items, size):
    return [items[x:x+size] for x in range(0, len(items), size)]

def getitem(items, index):
    try:
        return items[index]
    except (KeyError, IndexError):
        return ""

def twocol(items):
    max_len = max(len(i) for i in items) + 2
    rows = math.ceil(len(items) / 2)
    dl = divide(items, rows)
    out = out = box["ltop"] + max_len * box["horz"] + box["tsplit"] + max_len * box["horz"] + box["rtop"]
    for i in range(0, rows):
        out += "\n" + box["vert"] + getitem(dl[0], i).center(max_len) + box["vert"] + getitem(dl[1], i).center(max_len) + box["vert"]
    out += "\n" + box["lbot"] + max_len * box["horz"] + box["rtsplit"] + max_len * box['horz'] + box['rbot']
    return out

def threecol(items):
    max_len = max(len(i) for i in items) + 2
    rows = math.ceil(len(items) / 3)
    dl = divide(items, rows)
    mid = max_len * box["horz"]
    out = out = box["ltop"] + mid + box["tsplit"] + mid + box['tsplit'] + mid + box["rtop"]
    for i in range(0, rows):
        out += "\n" + box["vert"] + getitem(dl[0], i).center(max_len) + box["vert"] + getitem(dl[1], i).center(max_len) + box["vert"] + getitem(dl[2], i).center(max_len) + box["vert"]
    out += "\n" + box["lbot"] + mid + box["rtsplit"] + mid + box["rtsplit"] + mid +  box['rbot']
    return out

def col(items, columns=2):
    max_len = max(len(i) for i in items) + 2
    rows = math.ceil(len(items) / columns)
    dl = divide(items, rows)
    out = box["ltop"] + box["tsplit"].join([max_len * box["horz"]] * columns) + box["rtop"]
    for i in range(0, rows):
        out += "\n" + box["vert"] + box["vert"].join(getitem(dl[j], i).center(max_len) for j in range(0, columns)) + box["vert"]
    out += "\n" + box["lbot"] + box["rtsplit"].join([max_len * box["horz"]] * columns) + box["rbot"]
    return out

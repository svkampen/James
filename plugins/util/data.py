www_headers = {
    'User-Agent': 'Mozilla/5.0 (compatible) (Python 3.3, en_US) James/3.2 IRC bot'
}

def lineify(data, max_size=400):
    """ Split text up into IRC-safe lines. """
    
    lines = [item.rstrip() for item in data.split('\n')]
    for item in lines:
        if len(item) > max_size:
            index = lines.index(item)
            lines[index] = item[:item.rfind(' ',0,300)]
            lines.insert(index+1, item[item.rfind(' ',0,300)+1:])
    return lines
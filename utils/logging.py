import time

class Logger(object):
    """ Logger """
    def __init__(self, output='james.log'):
        self.logfile = open(output, 'a', encoding='utf-8')

    def log(self, data):
        timestamp = time.strftime("[%H:%M:%S] ")
        print(timestamp+data)
        self.logfile.write(timestamp+data+'\n')

    def close(self):
        self.logfile.close()
    

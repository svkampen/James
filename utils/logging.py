import time

class Logger(object):
    """ Logger """
    def __init__(self, output='james.log'):
        self.logfile = open(output, 'a')

    def log(self, data):
        timestamp = time.strftime("[%H:%M:%S] ")
        print(timestamp+data)
        self.logfile.write(timestamp+data.encode('utf-8')+'\n')

    def close(self):
        self.logfile.close()
    

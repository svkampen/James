"""
The logging class
"""
import time


class Logger(object):
    """ Logger """
    def __init__(self, output='james.log'):
        try:
            self.logfile = open(output, 'a', encoding='utf-8')
        except:
            self.logfile = open(output, 'a')

    def log(self, data):
        """ log and print data """
        timestamp = time.strftime("[%H:%M:%S] ")
        try:
            print((timestamp+data).encode('utf-8').decode('utf-8'))
        except:
            pass
        self.logfile.write(timestamp+data+'\n')

    def close(self):
        """ close the logfile """
        self.logfile.close()

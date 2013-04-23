class Logger(object):
    """ Logger """
    def __init__(self, output='../james.log'):
        self.logfile = open(output, 'a')

    def log(self, data):
        print(data)
        self.logfile.write(data.encode('utf-8')+'\n')

    def close(self):
        self.logfile.close()
    

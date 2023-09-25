from time import strftime
from os.path import isfile

def clean_log(logfile: str):
    '''
    clean_log(logfile): here the contents of logfile will be erased
    '''
    with open(logfile, 'r+') as logfile:
        logfile.seek(0)
        logfile.truncate()
        
    logfile.close()

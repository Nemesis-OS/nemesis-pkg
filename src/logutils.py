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

def append_to_log(content: str, logfile: str):
    '''
    append_to_log(content, logfile): appends content to logfile
    '''
    if isfile(logfile) == False:
        raise FileNotFoundError("libnpkg: logfile does not exist")
    
    with open(logfile, 'a+') as logfile:    
        contents = logfile.read().splitlines()
        logfile.seek(0)
        logfile.write(f"{strftime('%D %H:%M:%S')} {content}\n")
        logfile.truncate()

    logfile.close()

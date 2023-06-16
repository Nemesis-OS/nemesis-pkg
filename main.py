from os import mkdir, chdir
from os.path import isdir, isfile
from sys import argv, exit, path
from subprocess import check_output
try:
    from requests import get
    from requests.exceptions import MissingSchema, ConnectionError
except ImportError:
    print("error: requests not found..")
    exit(1)

disable_check_important_files = True
ANSI_CODES = []

def parse_config_file():
    global disable_check_important_files, ANSI_CODES
    if isfile("/etc/nemesis-pkg/config.py") == True:
        pass
    else:
        print("error: config file not found")
        
    chdir("/etc/nemesis-pkg")
    path.append("/etc/nemesis-pkg")
    import config

    if str(type(config.ANSI_CODES)) == "<class 'list'>" and len(config.ANSI_CODES) == 5:
        ANSI_CODES = config.ANSI_CODES
    else:
        print("config error.. ANSI_CODES is either missing or there are less than 5 numbers")

    if config.check_nessary_files == False:
        disable_check_important_files = False
    else:
        disable_check_important_files = True
    
VERSION = 0.1



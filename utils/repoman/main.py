'''
nemesis-rpoman: a simple tool to manage nemesis-pkg repos..
'''

import sys
from os import getuid
from os.path import isfile
from subprocess import check_output

t_col = ["\x1b[31m",
         "\x1b[32m",
         "\x1b[34m",
         "\x1b[0m"]

def sync_verified_repos():
    '''
    this function determines the list of verified repos
    '''
    if isfile("/etc/nemesis-pkg/verified_repos.json") is True:
        db = check_output(['curl', 'https://raw.githubusercontent.com/Nemesis-OS/nemesis-pkg/main/utils/repoman/repos.json', '-s']).decode('utf-8')
        with open("/etc/nemesis-pkg/verified_repos.json", 'r+', encoding="utf-8") as repo_cfg:
            if repo_cfg.read() == db:
                repo_cfg.close()
            else:
                repo_cfg.seek(0)
                repo_cfg.write(str(db))
                repo_cfg.truncate()
                repo_cfg.close()
    else:
        print("{}info{}: fetching list of verified repos".format(t_col[2], t_col[3]))
        db = check_output(['curl', 'https://raw.githubusercontent.com/Nemesis-OS/nemesis-pkg/main/utils/repoman/repos.json']).decode('utf-8')
        with open("/etc/nemesis-pkg/verified_repos.json", 'w', encoding="utf-8") as repo_db:
            repo_db.write(db)
        repo_db.close()

def parse_db():
    '''
    this function parses database...
    '''
        
if __name__ == "__main__":
    if getuid() == 0:
        pass
    else:
        print("{}error{}: please run this as root".format(t_col[0], t_col[3]))
        sys.exit(1)
        
    sync_verified_repos()

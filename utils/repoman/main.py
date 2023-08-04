'''
nemesis-rpoman: a simple tool to manage nemesis-pkg repos..
'''

import sys
from os import getuid
from os.path import isfile
from subprocess import check_output
from json import loads


t_col = ["\x1b[31m",
         "\x1b[32m",
         "\x1b[34m",
         "\x1b[0m"]

vrepos = []
repos = []
repo_count = 1

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
    global vrepos, repos
    '''
    this function parses database...
    '''
    with open('/etc/nemesis-pkg/verified_repos.json', 'r', encoding="utf-8") as vrdb:
        vrepos = loads(vrdb.read())

    repos = list(vrepos.keys())

def view_info():
    for i in repos:
        print("{}{}{}: {}{}{}".format(t_col[1], repo_count, t_col[3], t_col[2], vrepos[i]['ID'], t_col[3]))
        print("\t{}Description{}: {}".format(t_col[2], t_col[3], vrepos[i]['DESC']))
        print("\t{}Source{}: {}".format(t_col[2], t_col[3], vrepos[i]['COMMAND_TO_ADD'][3]))
        
if __name__ == "__main__":
    if getuid() == 0:
        pass
    else:
        print("{}error{}: please run this as root".format(t_col[0], t_col[3]))
        sys.exit(1)

    sync_verified_repos()
    parse_db()

    if sys.argv[1] == "v" or sys.argv[1] == "view":
        view_info()
    else:
        print('''nemesis-pkg-rpoman: a tool to manage repos
==========================================
[a]dd: add repository
[h]elp: show this page
[v]iew: view verified repos''')

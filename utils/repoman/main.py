'''
nemesis-rpoman: a simple tool to manage nemesis-pkg repos..
'''

import sys
from os import getuid
from os.path import isfile
from subprocess import check_output
from json import loads, dumps

t_col = ["\x1b[31m",
         "\x1b[32m",
         "\x1b[34m",
         "\x1b[0m"]

CONFIG = None

def sync_verified_repos():
    '''
    this function determines the list of verified repos
    '''
    if isfile("/etc/nemesis-pkg/verified_repos.json") is True:
        vdb = check_output(['curl', 'https://raw.githubusercontent.com/Nemesis-OS/nemesis-pkg/main/utils/repoman/repos.json', '-s']).decode('utf-8') # pylint: disable=line-too-long
        with open("/etc/nemesis-pkg/verified_repos.json", 'r+', encoding="utf-8") as repo_cfg:
            if repo_cfg.read() == vdb:
                repo_cfg.close()
            else:
                repo_cfg.seek(0)
                repo_cfg.write(str(vdb))
                repo_cfg.truncate()
                repo_cfg.close()
    else:
        print(f"{t_col[2]}info{t_col[3]}: fetching list of verified repos")
        vdb = check_output(['curl', 'https://raw.githubusercontent.com/Nemesis-OS/nemesis-pkg/main/utils/repoman/repos.json']).decode('utf-8') # pylint: disable=line-too-long
        with open("/etc/nemesis-pkg/verified_repos.json", 'w', encoding="utf-8") as repo_db:
            repo_db.write(vdb)
        repo_db.close()

def parse_db():
    '''
    this function parses database...
    '''
    with open('/etc/nemesis-pkg/verified_repos.json', 'r', encoding="utf-8") as vrdb:
        vrepo = loads(vrdb.read())
        vrdb.close()

    repo = list(vrepo.keys())

    return [vrepo, repo]

def view_info():
    '''
    the main function used for viewing info
    '''
    counter = 1
    for i in repos:
        print(f"{t_col[2]}{counter}{t_col[3]}: {vrepos[i]['ID']}:")
        print(f"\t{t_col[2]}Description{t_col[3]}: {vrepos[i]['DESC']}")
        print(f"\t{t_col[2]}Source{t_col[3]}: {vrepos[i]['COMMAND_TO_ADD']}")
        counter = counter+1

if __name__ == "__main__":
    if getuid() == 0:
        pass
    else:
        print(f"{t_col[0]}error{t_col[3]}: please run this as root")
        sys.exit(1)

    sync_verified_repos()
    vrepos = parse_db()[0]
    repos = parse_db()[1]
    parse_db()
    try:
        if sys.argv[1] == "v" or sys.argv[1] == "view":
            sync_verified_repos()
            view_info()
        elif len(sys.argv) == 2 and sys.argv[1] == "a" or sys.argv[1] == "add":
            print(f"{t_col[0]}error{t_col[3]}: parameter REPO_ID not found")
            sys.exit(1)
        elif len(sys.argv) == 3 and sys.argv[1] == "a" or sys.argv[1] == "add":
            if sys.argv[2] in repos:
                with open("/etc/nemesis-pkg/config.json" , 'r+', encoding='utf-8') as npkg_config:
                    CONFIG = loads(npkg_config.read())
                    if vrepos[sys.argv[2]]['COMMAND_TO_ADD'] in CONFIG['REPOS']:
                        print(f"{t_col[2]}note{t_col[3]}: repo {sys.argv[2]} already added")
                        npkg_config.close()
                    else:
                        print(f"{t_col[2]}note{t_col[3]}: adding {sys.argv[2]} repo")
                        CONFIG['REPOS'].append(vrepos[sys.argv[2]]['COMMAND_TO_ADD'])
                        npkg_config.seek(0)
                        npkg_config.write(dumps(CONFIG))
                        npkg_config.truncate()
                        npkg_config.close()
                        print(f"{t_col[1]}sucess{t_col[3]}: enabled {sys.argv[2]} repo")
            else:
                print(f"{t_col[0]}error{t_col[3]}: repo id {sys.argv[2]} unverified..")
        else:
            print('''nemesis-pkg-rpoman: a tool to manage repos
==========================================
[a]dd: add repository
[h]elp: show this page
[v]iew: view verified repos''')
    except IndexError:
        print('''nemesis-pkg-rpoman: a tool to manage repos
==========================================
[a]dd: add repository
[h]elp: show this page
[v]iew: view verified repos''')

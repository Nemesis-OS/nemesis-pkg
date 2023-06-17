#!/usr/bin/python3
from os import mkdir, chdir, getlogin
from os.path import isdir, isfile
from sys import argv, exit, path
from subprocess import check_output
from time import strftime
try:
    from requests import get
    from requests.exceptions import MissingSchema, ConnectionError
except ImportError:
    print("error: requests not found..")
    exit(1)

disable_check_important_files = True
ANSI_CODES = []
REPOLIST = []

def parse_config_file():
    global disable_check_important_files, ANSI_CODES, REPOLIST
    if isfile("/etc/nemesis-pkg/config.py") == True:
        pass
    else:
        print("error: config file not found")
        exit(1)
        
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

    REPOLIST = config.REPOS

def sync_packages(PKGLIST: list[list[str]]):
    if check_output("whoami") != b'root\n':
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: root user can only run update")
        exit(1)
    else:
        pass
    
    for i in range(0 , len(PKGLIST)):                
        fexists = False
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: updating {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]}")
        if isfile(f"/etc/nemesis-pkg/{PKGLIST[i][1]}") == True:
            fexists = True
            plist = open(f"/etc/nemesis-pkg/{PKGLIST[i][1]}" , 'r+')
            list_contents = plist.read()
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} not found so creating it..")
            plist = open(f"/etc/nemesis-pkg/{PKGLIST[i][1]}" , 'w')

        downloaded_version = get(PKGLIST[i][0]).content.decode("utf-8")

        if fexists == False:
            plist.write(str(downloaded_version))
            plist.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: made {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]}")
        elif list_contents != str(downloaded_version):
            plist.seek(0)
            plist.write(str(downloaded_version))
            plist.truncate()
            plist.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} up to date")
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} was up to date")

        ctime = strftime("%D %H:%M:%S")
        write_history(f"{ctime} {ANSI_CODES[2]}{PKGLIST[i][2]}{ANSI_CODES[4]} repo updated..")

def write_history(current_opr: str):
    history_npkg = False
    if isfile(f"/home/{getlogin()}/.nemesis-pkg_history") == True:
        history_npkg = True
        history = open(f"/home/{getlogin()}/.nemesis-pkg_history" , 'r+')
    else:
        history = open(f"/home/{getlogin()}/.nemesis-pkg_history" , 'w')

    if history_npkg == False:
        history.write(current_opr)
        history.close()
    else:
        history.seek(0)
        historyc = history.read()
        historyc = historyc + f"\n{current_opr}"
        history.write(historyc)
        history.truncate()
        history.close()

VERSION = 0.1
BUILD_NUM = 23617

if __name__ == "__main__":
    parse_config_file()
    try:
        if len(argv) > 1 and argv[1] == "update":
            sync_packages(REPOLIST)
        elif len(argv) > 1 and argv[1] == "version" or argv[1] == "-v":
            print(f"nemesis-pkg build {VERSION} {BUILD_NUM}")
        elif len(argv) > 1 and argv[1] == "history":
            file = open(f"/home/{getlogin()}/.nemesis-pkg_history")
            print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: this is the complete history of operations run by nemesis-pkg")
            print(file.read())
            file.close()
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")
    except IndexError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")

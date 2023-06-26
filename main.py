#!/usr/bin/python3
from os import mkdir, chdir, getlogin, system
from os.path import isdir, isfile
from sys import argv, exit, path
from subprocess import check_output, CalledProcessError
from shutil import copy
from time import strftime

#disable_check_important_files = True
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
            pass
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} not found so creating it..")
            plist = open(f"/etc/nemesis-pkg/{PKGLIST[i][1]}" , 'w')    
        downloaded_version = check_output(['curl' , PKGLIST[i][0]]).decode("utf-8")
        
        if fexists == False:
            plist.write(str(downloaded_version))
            plist.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: made {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]}")
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} UPDATE {PKGLIST[i][1]}")
        elif list_contents != str(downloaded_version):
            plist.seek(0)
            plist.write(str(downloaded_version))
            plist.truncate()
            plist.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} updated..")
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} UPDATE {PKGLIST[i][1]}")
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} was up to date")
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} UPDATE {PKGLIST[i][1]}")

def write_log(text: str):
    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: checking if log file found")
    if isfile("/etc/nemesis-pkg/nemesis-pkg.log") == True:
        log_not_there = False
        pass
    else:
        print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: the log file does not exists so creating it..")
        log_not_there = True

    if log_not_there == True:
        chdir("/etc/nemesis-pkg")
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log", 'w')
        logfile.write(f"{text}\n")
        logfile.close()
    else:
        chdir("/etc/nemesis-pkg")
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log", 'r+')
        logfile.seek(0)
        if logfile.read().splitlines == []:
            logfile.write(f"{text}\n")
        else:
            logfile.write(f"{text}\n")
        logfile.truncate()
        logfile.close()

VERSION = 0.1
BUILD_NUM = 23625

if __name__ == "__main__":
    parse_config_file()
    try:
        if len(argv) >= 2 and argv[1] == "sync":
            sync_packages(REPOLIST)
        elif len(argv) >= 2 and argv[1] == "version" or argv[1] == "-v":
            print(f"nemesis-pkg build {VERSION} {BUILD_NUM}")
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")
    except IndexError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")
    except KeyboardInterrupt:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user pressed CTRL+C so exiting")
        exit(1)

#!/usr/bin/python3
from os import mkdir, chdir, system, environ
from os.path import isdir, isfile
from sys import argv, exit, path
from subprocess import check_output, CalledProcessError
from shutil import copy
from time import strftime
from tomllib import loads, TOMLDecodeError

disable_check_important_files = False
preserve_build_files = True
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

    if config.preserve_build_files == True:
        preserve_build_files == True
    else:
        preserve_build_files == False


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

def view_log():
    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: viewing the nemesis-pkg log file")
    chdir("/etc/nemesis-pkg")
    try:
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log" , 'r')
        print(logfile.read())
        logfile.close()
    except FileNotFoundError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: file not found")

def remove_log():
    yn = str(input(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: removing the logfile will delete the list of all the operations you executed...[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}N{ANSI_CODES[4]}] "))
    if yn == "y" or yn == "Y":
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: removing logfile")
        chdir("/etc/nemesis-pkg")
        if system("rm nemesis-pkg.log") == 0:
            print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: the logfile was removed succesfully")
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: something went wrong that is why the logfile was not removed")
            exit(1)
    else:
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: the logfile was not deleted")

def list_packages():
    for i in range(0, len(REPOLIST)):
        file = open(f"/etc/nemesis-pkg/{REPOLIST[i][1]}" , 'r')
        for h in file.read().splitlines():
            print(str(f"{ANSI_CODES[2]}{REPOLIST[i][2]}{ANSI_CODES[4]}/{h.split()[0]} {ANSI_CODES[1]}{h.split()[1]}{ANSI_CODES[4]}"))

def install_packages(pname: str):
    print(f"{ANSI_CODES[3]}build{ANSI_CODES[4]}: downloading {pname}")
    preserve_build_files = False
    if preserve_build_files == False:
        mkdir(f"/tmp/nemesis-pkg-build/")
        mkdir(f"/tmp/nemesis-pkg-build/{pname}")
        chdir(f"/tmp/nemesis-pkg-build/{pname}")
    
    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: downloading build.toml")
    build_contents = check_output(['curl' , f'https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/{pname}/build']).decode('utf-8')
    try:
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: preparing source for {loads(build_contents)['core']['name']}@{loads(build_contents)['core']['version']}")
        system('git clone '+loads(build_contents)['core']['source']+f" {loads(build_contents)['core']['name']}")
        environ['NEMESIS_PKG_BUILD_DIR'] = loads(build_contents)['core']['name']
        system(loads(build_contents)['build']['command'])
        if system(loads(build_contents)['build']['command']) == 0:
            print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: {loads(build_contents)['core']['name']} installed sucessfully")
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {loads(build_contents)['core']['name']} installed unsucessfully")
    except TOMLDecodeError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} not in repositories")

VERSION = 0.1
BUILD_NUM = 23626

if __name__ == "__main__":
    parse_config_file()
    try:
        if len(argv) >= 2 and argv[1] == "sync":
            sync_packages(REPOLIST)
        elif len(argv) >= 2 and argv[1] == "version" or argv[1] == "-v":
            print(f"nemesis-pkg build {VERSION} {BUILD_NUM}")
        elif len(argv) >= 2 and argv[1] == "log":
            if len(argv) == 2:
                print("log: this allows you to view/delete logs\n========================================\nview: this allows you to view logfile\ndelete: this allows you to delete logfile")
            elif len(argv) == 3 and argv[2] == "view" or argv[2] == "v":
                view_log()
            elif len(argv) == 3 and argv[2] == "delete" or argv[2] == "d":
                remove_log()
            else:
                print("log: this allows you to view/delete logs\n========================================\nview: this allows you to view logfile\ndelete: this allows you to delete logfile")
        elif len(argv) >= 2 and argv[1] == "list":
            list_packages()
        elif len(argv) >=2 and argv[1] == "install":
            install_packages(argv[2])
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")

    except IndexError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")
    except KeyboardInterrupt:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user pressed CTRL+C so exiting")
        exit(1)

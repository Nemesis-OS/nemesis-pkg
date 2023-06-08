from sys import argv, exit 
from requests import get
from subprocess import check_output 
from os.path import isfile, isdir
from os import mkdir, chdir
from shutil import copy
from requests.exceptions import MissingSchema, ConnectionError

ANSI_CODES = [
    "\x1b[31m",
    "\x1b[32m",
    "\x1b[33m",
    "\x1b[34m",
    "\x1b[0m"
]

mainpage = """nemesis-pkg:
============
usage:- nemesis-pkg {operation} {args}
============
operations:-
i: installs a package.. nemesis-pkg i {pkg1} {pkg2}
r: removes a package... nemesis-pkg r {pkg1} {pkg2}
lsi: lists system installed packages.. nemesis-pkg lsi {pkg}
lri: lists packages in repository... nemesis-pkg lri {pkg}
ug: upgrade packages... nemesis-pkg ug
ud: update the package database... nemesis-pkg ud
h: shows info on operations and usage.. nemesis-pkg h
v: show nemesis-pkg version"""

operations = ["i" , "r" , "lsi" , "lri" , "ug" , "ud" , "h" , "v"]
path_pkglist = "/etc/nemesis-pkg/PKGLIST"
path_ipkglist = "/etc/nemesis-pkg/IPKGLIST"
current_user = check_output(["whoami"])
pkglist_src = "https://raw.githubusercontent.com/Nemesis-OS/packages/main/PKGLIST"
cmd_args = []

def update_database():
    if isfile(path_pkglist) == True:
        local_PKGLIST = True
        pass
    else:
        local_PKGLIST = False
        print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: database file is not found on path so downloading it")
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: creating database file")
        if isdir("/etc/nemesis-pkg") == False:
            mkdir("/etc/nemesis-pkg")
        pass

    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: downloading database..")
    try:
        new_PKGLIST = get(pkglist_src)
    except ConnectionError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: file failed to download due to connectivity issue")
        exit(1)
    except MissingSchemasingSchema:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: file failed to download due to some exceptions")
        exit(1)

    if new_PKGLIST != None and local_PKGLIST == False:
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: creating PKGLIST..")
        local_PKGLIST = open(path_pkglist, 'w')
        local_PKGLIST.write(str(new_PKGLIST.content.decode("utf-8")))
        local_PKGLIST.close()
    else:
        local_PKGLIST = open(path_pkglist, 'r+')
        if local_PKGLIST.read() != str(new_PKGLIST.content.decode("utf-8")):
            print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: replacing PKGLIST with the new one")
            local_PKGLIST.seek(0)
            local_PKGLIST.write(str(new_PKGLIST.content.decode("utf-8")))
            local_PKGLIST.truncate()
            local_PKGLIST.close()
            pass
        else:
            print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: you had the latest database")

    print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}:- the databases were updated succesfully")

def list_packages_from_repo(query: list[str]):
    print(f"{ANSI_CODES[3]}info:{ANSI_CODES[4]} syncing the databases to get latest software")
    update_database()
    PKGLIST = open(path_pkglist , "r+")
    PKGLIST_AVAILABLE = PKGLIST.read()
    PKGLIST_AVAILABLE = PKGLIST_AVAILABLE.splitlines()
    if query == []:
        print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: no query specified so printing the list of available packages")
        for i in PKGLIST_AVAILABLE:
            print(i)
    else:
        for i in range(0 , len(query)):
            pkgs_matching = []
            qry = list(query[i])
            for j in PKGLIST_AVAILABLE:
                if j.find(qry[i]) == -1:
                    continue
                else:
                    pkgs_matching.append(j)
                    continue
                    
            if pkgs_matching == []:
                print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no package was relevant to {query[i]}")
            else:
                print(f"{ANSI_CODES[2]}note{ANSI_CODES[4]}: there were some packages matching to {query[i]}..")
                for matching_pkgs in pkgs_matching:
                    print(matching_pkgs)

            continue

def list_installed_packages(query: list[str]):
    installed_packages = open(path_ipkglist, 'r')
    installed_packages_content = installed_packages.read()
    install_packages_content = installed_packages_content.splitlines()
    if query == []:
        for i in install_packages_content:
            print(i)
    else:
        for i in range(0, len(query)):
            print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: checking if {query[i]} is installed or not")
            if query[i] in install_packages_content:
                print(f"{ANSI_CODES[2]}note{ANSI_CODES[4]}: {query[i]} is installed")
            else:
                print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {query[i]} is not installed")

def check_if_important_files_are_there():
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: nemesis-pkg is checking that some important files are there or not...")
    if isdir("/etc/nemesis-pkg") == True and isfile("/etc/nemesis-pkg/IPKGLIST") == True and isfile("/etc/nemesis-pkg/PKGLIST") == True:
        print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: the neccesary files are present in the system")
    else:
        print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: some files were not found so nemesis-pkg is creating it")
        
    if isdir("/etc/nemesis-pkg") == False:
        mkdir("/etc/nemesis-pkg/")
    else:
        pass

    if isfile("/etc/nemesis-pkg/PKGLIST") == False:
        file = open("/etc/nemesis-pkg/PKGLIST" , 'w')
        file.write('')
        file.close()
    else:
        pass
        
    if isfile("/etc/nemesis-pkg/IPKGLIST") == False:
        file = open("/etc/nemesis-pkg/IPKGLIST" , 'w')
        file.write('')
        file.close()
    else:
        pass

def upgrade_packages():
    print("info: in order to check for the latest packages the database needs to be synced")
    update_database()
    read_PKGLIST = open("/etc/nemesis-pkg/PKGLIST")
    read_IPKGLIST = open("/etc/nemesis-pkg/IPKGLIST" , 'r+')
    content_PKGLIST = read_PKGLIST.read()
    content_IPKGLIST = read_IPKGLIST.read()
    packages_to_update = []
    for i in range(0, len(content_PKGLIST)):
        content_PKGLIST[i].split()
    for i in range(0, len(content_IPKGLIST)):
        content_IPKGLIST.[i].split()
    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: the following packages need to be updated")
    

if __name__ == "__main__":
    if current_user != b'root\n':
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(1)
    else:
        pass

    check_if_important_files_are_there()
    
    try:
        if argv[1] == "h":
            print(mainpage)
        elif argv[1] == "v":
            print("nemesis-pkg 0.1(Build 2368)")
        elif argv[1] == "ud":
            update_database()
        elif argv[1] == "ug":
            upgrade_packages()
        elif argv[1] == "lri":
            for i in range(2, len(argv)):
                cmd_args.append(argv[i])
            list_packages_from_repo(cmd_args)
        elif argv[1] == "lsi":
            for i in range(2, len(argv)):
                cmd_args.append(argv[i])
            list_installed_packages(cmd_args)
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")
    except IndexError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")

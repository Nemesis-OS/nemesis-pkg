from sys import argv, exit 
from requests import get
from subprocess import check_output 
from os.path import isfile 
from shutil import copy
from requests.exceptions import MissingSchema, ConnectionError

mainpage = """
nemesis-pkg:
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
v: show nemesis-pkg version
"""
operations = ["i" , "r" , "lsi" , "lri" , "ug" , "ud" , "h" , "v"]
path_pkglist = "/etc/nemesis-pkg/PKGLIST"
path_ipkglist = "/etc/nemesis-pkg/IPKGLIST"
current_user = check_output(["whoami"])
pkglist_src = "https://raw.githubusercontent.com/Nemesis-OS/packages/main/PKGLIST"

def update_database():
    if isfile(path_pkglist) == True:
        local_PKGLIST = True
        pass
    else:
        local_PKGLIST = False
        print("warning: database file is not found on path so downloading it")
        pass

    print("info: downloading database..")
    try:
        new_PKGLIST = get(pkglist_src)
    except ConnectionError:
        print("error: file failed to download due to connectivity issue")
    except MissingSchema:
        print("error: file failed to download due to some exceptions")

    if new_PKGLIST != None and local_PKGLIST == True:
        print("info: creating PKGLIST..")
        local_PKGLIST = open(path_pkglist, 'w')
        local_PKGLIST.write(str(new_PKGLIST.content.decode("utf-8")))
        local_PKGLIST.close()
    else:
        local_PKGLIST = open(path_pkglist, 'r+')
        if local_PKGLIST.read() != str(new_PKGLIST.content.decode("utf-8")):
            print("info: replacing PKGLIST with the new one")
            local_PKGLIST.seek(0)
            local_PKGLIST.write(str(new_PKGLIST.content.decode("utf-8")))
            local_PKGLIST.truncate()
            pass
        else:
            print("info: you had the latest database")

    print("sucess:- the databases were updated succesfully")
        
if __name__ == "__main__":
    if current_user != b'root\n':
        print("error: user is not root")
        exit(1)
    else:
        pass
    
    try:
        if argv[1] == "h":
            print(mainpage)
        elif argv[1] == "v":
            print("nemesis-pkg 0.1(Build 2361)")
        elif argv[1] == "ud":
            update_database()
        else:
            print("error: invalid operation")
    except IndexError:
        print("error: no operation specified")

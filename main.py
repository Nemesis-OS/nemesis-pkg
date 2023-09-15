#!/usr/bin/python3
from os import mkdir, chdir, system, environ
from os.path import isfile
from sys import argv, path, exit
from subprocess import check_output, CalledProcessError
from time import strftime
from json import loads, dumps
from json.decoder import JSONDecodeError

npkg_cc = "gcc"  # let gcc be the default cc
npkg_cxx = "g++"  # let g++ be the default cxx
npkg_mkopts = "-j$(nproc)"  # nproc returns amount of cores so..
npkg_cflags = "-march=native -O3 -pipe"  # flags for your c compiler...
npkg_cxxflags = "-march=native -O3 -pipe"  # flags for your c++ compiler.
disable_check_important_files = False
pbf = False
ANSI_CODES = ['\x1b[31m', '\x1b[32m', '\x1b[33m', '\x1b[34m', '\x1b[0m']
REPOLIST = []
CPU_FLAGS = []
on_search_mode = False
upgrade_pkg = False
pkg_cache_ex = False

def check_user_is_root():
    user = check_output('whoami')
    if user == b'root\n':
        return bool(True)
    else:
        return bool(False)


def parse_config_file():
    global disable_check_important_files, ANSI_CODES, REPOLIST, cpu_flags, pbf, npkg_cc, npkg_cxx, npkg_mkopts, npkg_cflags, npkg_cxxflags
    if isfile("/etc/nemesis-pkg/config.json") is True:
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: config file not found")
        exit(1)

    with open("/etc/nemesis-pkg/config.json", 'r', encoding="utf-8") as ncfg:
        config = loads(ncfg.read())

    ncfg.close()

    REPOLIST = config['REPOS']

    if config['SAVE_BUILD_FILES'] is True:
        pbf = True
    else:
        pbf = False

    if not config['CPU_FLAGS']:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: cpu flags is not defined")
    else:
        cpu_flags = config['CPU_FLAGS']

    if "CC" in list(config.keys()):
        npkg_cc = config["CC"]

    if "CXX" in list(config.keys()):
        npkg_cxx = config["CXX"]

    if "MAKEOPTS" in list(config.keys()):
        npkg_mkopts = config["MAKEOPTS"]

    if "CFLAGS" in list(config.keys()):
        npkg_cflags = config["CFLAGS"]

    if "CXXFLAGS" in list(config.keys()):
        npkg_cxxflags = config["CXXFLAGS"]

    environ["CC"] = npkg_cc
    environ["CXX"] = npkg_cxx
    environ["MAKEOPTS"] = npkg_mkopts
    environ["CFLAGS"] = npkg_cflags
    environ["CXXFLAGS"] = npkg_cxxflags

def sync_database():
    if check_user_is_root() == True:
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: user not root")
        exit(1)

    for i in list(REPOLIST.keys()):
        try:
            web_contents = check_output(["curl", REPOLIST[i], '-s']).decode("utf-8")
        except CalledProcessError:
            print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: database for repo {ANSI_CODES[2]}{i}{ANSI_CODES[4]} failed to download")
            continue

        if isfile(f"/etc/nemesis-pkg/{i}.PKGLIST") == True:
            with open(f"/etc/nemesis-pkg/{i}.PKGLIST", 'r+') as rpofile:
                contents = rpofile.read()
                if contents == web_contents:
                    rpofile.close()
                    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: database for repo {ANSI_CODES[2]}{i}{ANSI_CODES[4]} up to date")
                else:
                    rpofile.seek(0)
                    rpofile.write(web_contents)
                    rpofile.truncate()
                    rpofile.close()
                    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: database for repo {ANSI_CODES[2]}{i}{ANSI_CODES[4]} updated")
        else:
            with open(f"/etc/nemesis-pkg/{i}.PKGLIST", 'w') as rpofile:
                rpofile.write(web_contents)
                rpofile.close()

            print(f"=> {ANSI_CODES[2]}note{ANSI_CODES[4]}: made database for repo {ANSI_CODES[2]}{i}{ANSI_CODES[4]}")

def write_log(text: str):
    if isfile("/etc/nemesis-pkg/nemesis-pkg.log") == True:
        log_not_there = False
        pass
    else:
        log_not_there = True

    if log_not_there == True:
        chdir("/etc/nemesis-pkg")
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log", 'w')
        logfile.write(f"{text}")
        logfile.close()
    else:
        chdir("/etc/nemesis-pkg")
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log", 'r+')
        logfile.seek(0)
        if logfile.read().splitlines == []:
            logfile.write(f"{text}")
        else:
            logfile.write(f"\n{text}")
        logfile.truncate()
        logfile.close()

def view_log():
    print(f"=> {ANSI_CODES[3]}info{ANSI_CODES[4]}: viewing the nemesis-pkg log file")
    chdir("/etc/nemesis-pkg")
    try:
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log" , 'r', encoding="utf-8")
        print(logfile.read())
        logfile.close()
    except FileNotFoundError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: file not found")

def remove_log():
    if check_user_is_root() == True:
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(1)

    yn = str(input(f"=> {ANSI_CODES[2]}warning{ANSI_CODES[4]}: removing the logfile will delete the list of all the operations you executed...[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}N{ANSI_CODES[4]}] "))
    if yn in ["Y", 'y']:
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: removing logfile")
        chdir("/etc/nemesis-pkg")
        if system("rm nemesis-pkg.log") == 0:
            print(f"=> {ANSI_CODES[1]}sucess{ANSI_CODES[4]}: the logfile was removed succesfully")
        else:
            print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: something went wrong that is why the logfile was not removed")
            exit(1)
    else:
        print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: the logfile was not deleted")

def list_packages():
    for i in list(REPOLIST.keys()):
        file = open(f"/etc/nemesis-pkg/{i}.PKGLIST" , 'r')
        for h in file.read().splitlines():
            print(str(f"=> {ANSI_CODES[2]}{i}{ANSI_CODES[4]}/{h.split()[0]} {ANSI_CODES[1]}{h.split()[1]}{ANSI_CODES[4]}"))


def install_multiple_packages(pkglist: list[str]):
    if check_user_is_root():
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(1)

    for i in pkglist:
        install_packages(i)

def install_packages(pname: str):
    global pkg_cache_ex
    if check_user_is_root() is True:
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(1)

    install_source = {}
    repo_name = ""
    reinstall_yn = None

    if return_if_pkg_exist(pname) == False:
        pass
    else:
        reinstall_yn = input(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} is installed.. do you wanna reinstall[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}n{ANSI_CODES[4]}] ")
        if reinstall_yn in ('n', 'N'):
            return None
        else:
            pass
    
    if reinstall_yn in ("Y", "y"):
        with open("/etc/nemesis-pkg/installed-packages.PKGLIST", 'r') as ipkgl:
            repo_name = loads(ipkgl.read())[pname]["repo"]

        ipkgl.close()

    if pbf is False:
        try:
            mkdir("/tmp/nemesis-pkg-build/")
        except FileExistsError:
            pass

        try:
            mkdir(f"/tmp/nemesis-pkg-build/{pname}")
        except FileExistsError:
            system(f"rm -rf /tmp/nemesis-pkg-build/{pname}")
            mkdir(f"/tmp/nemesis-pkg-build/{pname}")
            chdir(f"/tmp/nemesis-pkg-build/{pname}")
            pass
    else:
        try:
            mkdir("/var/cache/nemesis-pkg")
        except FileExistsError:
            pass

        try:
            mkdir(f"/var/cache/nemesis-pkg/{pname}")
        except FileExistsError:
            yn = input(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: cache for {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} exists... use it?[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}N{ANSI_CODES[4]}] ")
            if yn in ("y", "Y", "Yes", "yes"):
                pkg_cache_ex = True
                print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: using cache")
            else:
                system(f"rm -rf /var/cache/nemesis-pkg/{pname}")
                mkdir(f"/var/cache/nemesis-pkg/{pname}")

        chdir(f"/var/cache/nemesis-pkg/{pname}")

    curl = ""

    if pkg_cache_ex == False:
        print(f"=> {ANSI_CODES[3]}build{ANSI_CODES[4]}: checking if {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} in repos.")

        for i in list(REPOLIST.keys()):
            src = REPOLIST[i].split("/")
            src.pop(src.__len__()-1)
            crepo_src = ""

            for url in src:
                if url == "https:":
                    crepo_src = crepo_src+url+"//"
                else:
                    crepo_src = crepo_src+url+"/"
            
            current_db = open(f"/etc/nemesis-pkg/{i}.PKGLIST", 'r')
            
            for j in current_db.read().split():
                if j.split()[0] in pname:
                    if i in list(install_source.keys()):
                        pass
                    else:
                        install_source[i] = crepo_src
                    current_db.close()
                else:
                    current_db.close()
                    continue

            current_db.close()
            continue

        if install_source == {}:
            print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} not in repos")
            exit(1)
        else:
            pass

        if len(list(install_source.keys())) == 1:
            repo_name = list(install_source.keys())[0]
            curl = install_source[list(install_source.keys())[0]]+pname+"/build"
        else:
            print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: pkg {pname} found in multiple repos")
            for i in list(install_source.keys()):
                print(i)
            repo_choice = input(f"=> {ANSI_CODES[3]}input{ANSI_CODES[4]}: {pname} should be installed from which repo? ")
            if repo_choice not in list(install_source.keys()):
                print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: repo {repo_choice} not enabled")
                exit(1)
            else:
                repo_name = repo_choice
                curl = install_source[repo_choice]+pname+"/build"

    if pkg_cache_ex == False:
        try:
            print(f"=> {ANSI_CODES[3]}info{ANSI_CODES[4]}: downloading build.json")
            build_contents = check_output(['curl' , curl, "-o", "build.json"]).decode('utf-8')
        except CalledProcessError:
            print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}build.json{ANSI_CODES[4]} failed to download")
            exit(1)
    
    build_contents = open("build.json", 'r')
    build_contents = build_contents.read()

    if build_contents == "404: Not Found":
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}build.json{ANSI_CODES[4]} failed to download")
        exit(1)

    try:
        if loads(build_contents)['core']['cpu_flags'] == []:
            pass
        else:
            print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: checking if your cpu has neccesary instruction sets")
            for i in loads(build_contents)['core']['cpu_flags']:
                if i in cpu_flags:
                    pass
                else:
                    print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {i} not in cpu flags")
                    exit(1)
	
        if pkg_cache_ex == False:
            print(f"=> {ANSI_CODES[3]}info{ANSI_CODES[4]}: preparing source for {loads(build_contents)['core']['name']}@{loads(build_contents)['core']['version']}")
            system(f"git clone {loads(build_contents)['core']['source']} {loads(build_contents)['core']['name']}")

        if loads(build_contents)['core']['depends'] == []:
            print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: {pname} has no dependencies so installing it")
            pass
        else:
            for i in loads(build_contents)['core']['depends']:
                print(f"=> {ANSI_CODES[2]}info{ANSI_CODES[4]}: installing dependency {i} for {pname}")
                install_packages(i)

        if pbf == False:
            environ['NEMESIS_PKG_BUILD_DIR'] = f"/tmp/nemesis-pkg-build/{loads(build_contents)['core']['name']}/{loads(build_contents)['core']['name']}"
        else:
            environ['NEMESIS_PKG_BUILD_DIR'] = f"/var/cache/nemesis-pkg/{loads(build_contents)['core']['name']}/{loads(build_contents)['core']['name']}"
        print(f"=> {ANSI_CODES[2]}info{ANSI_CODES[4]}: installing {pname}")
        if system(loads(build_contents)['build']['command']) == 0:
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} PASS {pname} installed sucesfully")
            print(f"=> {ANSI_CODES[1]}sucess{ANSI_CODES[4]}: {loads(build_contents)['core']['name']} installed sucessfully")
            if isfile("/etc/nemesis-pkg/installed-packages.PKGLIST") == True:
                with open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'r+', encoding="utf-8") as installed_pkgs:
                    pkg_hmap = loads(installed_pkgs.read())
                    pkg_hmap[f'{pname}'] = {"version": loads(build_contents)['core']['version'], "file_list": loads(build_contents)['build']['files'], "dependencies": loads(build_contents)['core']['depends'], "repo": repo_name}
                    installed_pkgs.seek(0)
                    installed_pkgs.write(dumps(pkg_hmap))
                    installed_pkgs.truncate()
                installed_pkgs.close()
            else:
                with open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'w', encoding="utf-8") as installed_pkgs:
                    pkg_hmap = {}
                    pkg_hmap[f'{pname}'] = {"version": loads(build_contents)['core']['version'], "file_list": loads(build_contents)['build']['files'], "dependencies": loads(build_contents)['core']['depends'], "repo": repo_name}
                    installed_pkgs.write(dumps(pkg_hmap))
                installed_pkgs.close()
        else:
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} ERROR {pname} failed to install")
            print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: {loads(build_contents)['core']['name']} installed unsucessfully")
            exit(1)
    except (KeyError):
        ctime = strftime("%D %H:%M:%S")
        write_log(f"{ctime} ERROR {pname} failed to install")
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: either this package is missing or the build file is corrupt... please open a bug report to the NemesisOS Developers regarding this issue.")


def list_installed():
    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: this is the list of all installed packages")
    try:
        with open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'r', encoding="utf-8") as ipkglist_open:
            contents = loads(ipkglist_open.read())
            pkgs = list(contents.keys())
            pkgs.sort()
            for installed_pkgs in pkgs:
                print(f"=> {ANSI_CODES[2]}{installed_pkgs}{ANSI_CODES[4]}@{ANSI_CODES[1]}{contents[installed_pkgs]['version']}{ANSI_CODES[4]}")

            ipkglist_open.close()
    except AttributeError:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: something went wrong")

def list_repos():
    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: the available repositories are:")
    for i in list(REPOLIST.keys()):
        print(f"=> {ANSI_CODES[2]}{i}{ANSI_CODES[4]}")

def list_pkgs_from_repo(rname: str):
    if rname in list(REPOLIST.keys()):
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}{rname}{ANSI_CODES[4]} is not a valid repository.")
        exit(1)

    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: showing the list of packages in {ANSI_CODES[2]}{rname}{ANSI_CODES[4]}")
    rpofile_open = open(f"/etc/nemesis-pkg/{rname}.PKGLIST" , 'r')
    for i in rpofile_open.read().splitlines():
        print(f"=> {ANSI_CODES[2]}{i.split()[0]}{ANSI_CODES[4]}@{ANSI_CODES[1]}{i.split()[1]}{ANSI_CODES[4]}")


def uninstall_new(query: str):
    if check_user_is_root() is True:
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(0)

    if return_if_pkg_exist(query=query) == True:
        pass
    else:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: {query} not installed")
        exit(1)

    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: removing {query}")
    installed_database = None
    ipkgl =  open("/etc/nemesis-pkg/installed-packages.PKGLIST", 'r+', encoding="utf-8")
    installed_database = loads(ipkgl.read())
    pkg_depending_in_query = []

    for i in list(installed_database.keys()):
        if query in installed_database[i]['dependencies']:
            pkg_depending_in_query.append(i)
        else:
            continue
    if pkg_depending_in_query == []:
        for i in installed_database[query]["file_list"]:
            if system(f"rm -rf {i}") == 0:
                continue
            else:
                print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: {query} failed to uninstall")
                exit(1)

        installed_database.pop(query)
        ipkgl.seek(0)
        ipkgl.write(dumps(installed_database))
        ipkgl.truncate()
        ipkgl.close()
        print(f"=> {ANSI_CODES[1]}sucess{ANSI_CODES[4]}: {query} uninstalled")
    else:
        for i in pkg_depending_in_query:
            print(i)

        inp = input(f"=> {ANSI_CODES[2]}warning{ANSI_CODES[4]}: these packages will be removed[y/N]? ")
        if inp == "y" or inp == "Y":
            for i in pkg_depending_in_query:
                uninstall_new(i)
            uninstall_new(query=query)
        else:
            print(f"{ANSI_CODES[2]}note{ANSI_CODES[4]}: operation cancelled")
            exit(1)

def uninstall_multiple(plist: list[str]):
    for i in plist:
        uninstall_new(i)

def return_if_pkg_exist(query: str):
    try:
        with open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'r') as pkglist:
            a = list(loads(pkglist.read()).keys())
            if query in a:
                pkglist.close()
                return True
            else:
                pkglist.close()
                return False
    except (FileNotFoundError, IndexError, JSONDecodeError):
        return False

def search_package(query: str):
    global on_search_mode
    on_search_mode = True
    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: looking for pkgs matching to {ANSI_CODES[2]}{query}{ANSI_CODES[4]}")
    arr = []
    for repo_files in list(REPOLIST.keys()):
        file = open(f"/etc/nemesis-pkg/{repo_files}.PKGLIST", 'r', encoding="utf-8")
        for pkg in file.read().splitlines():
            chars = []
            for let in range(0, len(query)):
                if query in arr:
                    pass
                elif query[let] in pkg.split()[0]:
                    chars.append(query[let])

            if len(chars) == len(query) and pkg.split()[0] not in arr:
                arr.append([pkg.split()[0], pkg.split()[1]])
            else:
                pass

        file.close()

    arr.sort()
    if arr != []:
        for matching in arr:
            if return_if_pkg_exist(matching[0]) == True:
                print(f"=> {ANSI_CODES[2]}{matching[0]}{ANSI_CODES[4]}@{ANSI_CODES[3]}{matching[1]}{ANSI_CODES[0]}{ANSI_CODES[1]}[installed]{ANSI_CODES[4]}")
            else:
                print(f"=> {ANSI_CODES[2]}{matching[0]}{ANSI_CODES[4]}@{ANSI_CODES[3]}{matching[1]}{ANSI_CODES[4]}")
    else:
        print(f"=> {ANSI_CODES[2]}warning{ANSI_CODES[4]}: nothing similar to {query}")

def version_to_int(version: str):
    version = version.split(".")
    v2 = ""
    for i in version:
        v2 = v2+i

    return int(v2)

def upgrade_packeges():
    global upgrade_pkg
    pkg_upgrade = False
    print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: checking for upgradable packages")
    upgrade_pkg = False
    installed_pkgs = open("/etc/nemesis-pkg/installed-packages.PKGLIST", 'r')
    repo_pkgf = {}
    for i in list(REPOLIST.keys()):
        repo_pkgf[i] = f"{i}.PKGLIST"

    test = loads(installed_pkgs.read())

    for i in list(test.keys()):
        with open(f"/etc/nemesis-pkg/{repo_pkgf[test[i]['repo']]}", 'r') as pkdb:
            data = pkdb.read().split()
            if i in data:
                if version_to_int(data[data.index(i)+1]) > version_to_int(test[i]['version']):
                    print(f"=> {i} {ANSI_CODES[0]}{test[i]['version']}{ANSI_CODES[4]} -> {ANSI_CODES[1]}{data[data.index(i)+1]}{ANSI_CODES[4]}")
                    pkg_upgrade = True
            else:
                continue

        pkdb.close()

    if pkg_upgrade == False:
        print(f"=> {ANSI_CODES[3]}note{ANSI_CODES[4]}: system upto date")
    else:
        pass

VERSION = 0.1
BUILD_ID = "-rc1"

if __name__ == "__main__":
    parse_config_file()
    try:
        if len(argv) >= 2 and argv[1] in ("S", "sync"):
            sync_database()
        elif len(argv) >= 2 and argv[1] in ("v", "version"):
            print(f"nemesis-pkg build {VERSION}{BUILD_ID}")
        elif len(argv) >= 2 and argv[1] in ("log", "Log", "L"):
            if len(argv) == 2:
                print('''log: this allows you to view/delete logs
========================================
[v]iew: this allows you to view logfile
[d]elete: this allows you to delete logfile''')
            elif len(argv) == 3 and argv[2] in ("view", "v"):
                view_log()
            elif len(argv) == 3 and argv[2] in ("delete", "d"):
                remove_log()
            else:
                print('''log: this allows you to view/delete logs
========================================
view: this allows you to view logfile
delete: this allows you to delete logfile''')
        elif len(argv) >= 2 and argv[1] in ("l", "list"):
            if len(argv) == 3 and argv[2] == "installed":
                list_installed()
            elif len(argv) == 3 and argv[2] == "repos":
                list_repos()
            elif len(argv) == 3 and argv[2] == "help":
                print('''list: this allows you to list packages/repos
============================================
installed: shows the installed packages and their versions
repos: shows the list of repositories
repo_name: shows the list of packages in repo_name
default: shows the list of all packages in every repo''')
            elif len(argv) == 3 and argv[2] == "default":
                list_packages()
            elif len(argv) == 3:
                list_pkgs_from_repo(argv[2])
            else:
                list_packages()
        elif len(argv) >=2 and argv[1] in ("i", "install"):
            if len(argv) == 3:
                install_packages(argv[2])
            else:
                a = []
                for i in range(2, len(argv)):
                    a.append(argv[i])
                install_multiple_packages(a)
        elif len(argv) >= 2 and argv[1] in ("u", "uninstall"):
            if len(argv) == 3:
                uninstall_new(argv[2])
            else:
                a = []
                for i in range(2, len(argv)):
                    a.append(argv[i])
                uninstall_multiple(a)
        elif len(argv) >= 2 and argv[1] in ("s", "search"):
            search_package(argv[2])
        elif len(argv) == 2 and argv[1] in ("h", "help"):
            print('''nemesis-pkg help:
===================
[h]elp - Show this page
[i]nstall - Install a package
[l]ist - View package list
[L]og - View nemesis-pkg log
[s]earch - Search packages present
[S]ync - Sync package database
[u]ninstall - Uninstall a package
[U]pgrade - Upgrade packages''')
        elif len(argv) == 2 and argv[1] in ("U", "upgrade", "Upgrade"):
            upgrade_packeges()
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")

    except IndexError:
        print(f"=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")
    except KeyboardInterrupt:
        print(f"\n=> {ANSI_CODES[0]}error{ANSI_CODES[4]}: ctrl-c detection..")
        exit(1)

#!/usr/bin/python3
from os import mkdir, chdir, system, environ
from os.path import isfile
from sys import argv, path, exit
from subprocess import check_output, CalledProcessError
from time import strftime
from tomllib import loads, TOMLDecodeError
from ast import literal_eval

disable_check_important_files = False
preserve_build_files = False
ANSI_CODES = []
REPOLIST = []
cpu_flags = []

def check_user_is_root():
    cuser = check_output('whoami')
    if cuser == b'root\n':
        return True
    else:
        return False

def parse_config_file():
    global disable_check_important_files, ANSI_CODES, REPOLIST, cpu_flags, preserve_build_files
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

    if config.check_necessary_files == False:
        disable_check_important_files = False
    else:
        disable_check_important_files = True

    REPOLIST = config.REPOS

    if config.preserve_build_files == True:
        preserve_build_files = True
    else:
        preserve_build_files = False

    if config.cpu_flags == []:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: cpu flags is not defined")
    else:
        config.cpu_flags = cpu_flags
def sync_packages(PKGLIST: list[list[str]]):
    if check_output("whoami") != b'root\n':
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: root user can only run update")
        exit(1)
    else:
        pass
    
    for i in range(0 , len(PKGLIST)):                
        fexists = False
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: updating {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]}")
        if isfile(f"/etc/nemesis-pkg/{PKGLIST[i][1]}") is True:
            fexists = True
            plist = open(f"/etc/nemesis-pkg/{PKGLIST[i][1]}" , 'r+')
            list_contents = plist.read()
            pass
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} not found so creating it..")
            plist = open(f"/etc/nemesis-pkg/{PKGLIST[i][1]}" , 'w', encoding="utf-8")    
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
    if isfile("/etc/nemesis-pkg/nemesis-pkg.log") == True:
        log_not_there = False
        pass
    else:
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
    if check_user_is_root() == True:
        pass
    else:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(1)
        
    yn = str(input(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: removing the logfile will delete the list of all the operations you executed...[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}N{ANSI_CODES[4]}] "))
    if yn in ["Y", 'y']:
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
            
def install_multiple_packages(pkglist: list[str]):
    if check_user_is_root() == True:
        pass
    else:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(1)
        
    for i in pkglist:
        install_packages(i)
  
def install_packages(pname: str):
    if check_user_is_root() is True:
        pass
    else:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(1)

    pkg_in_repo = False
    pkg_in_w_repo = False
    reinstall_mode = False
    
    if return_if_pkg_exist(pname) is None:
        pass
    else:
        reinstall_yn = input(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} is installed.. do you wanna reinstall[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}n{ANSI_CODES[4]}] ")
        if reinstall_yn in ('n', 'N'):
            return None
        else:
            pass
        
    if preserve_build_files is False:
        try:
            mkdir(f"/tmp/nemesis-pkg-build/")
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
            system(f"rm -rf /var/cache/nemesis-pkg/{pname}")
            mkdir(f"/var/cache/nemesis-pkg/{pname}")

        chdir(f"/var/cache/nemesis-pkg/{pname}")
        
    curl = ""

    print(f"{ANSI_CODES[3]}build{ANSI_CODES[4]}: checking if {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} is in repositories..")
    for i in range(0, len(REPOLIST)):
        current_db = open(f"/etc/nemesis-pkg/{REPOLIST[i][1]}", 'r', encoding="utf-8")
        for j in current_db.read().splitlines():
            if j.split()[0] in pname:
                pkg_in_repo = True
                pkg_in_w_repo = REPOLIST[i]
                curl = f"{REPOLIST[i][3]}{pname}/build"
                current_db.close()
            else:
                pkg_in_repo = False
                current_db.close()                
                continue

        current_db.close()
        if pkg_in_repo is True:
            continue
        else:
            continue
        
    if curl is "":
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} is not in any repositories")
        exit(1)
    else:
        pass

    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: downloading build.toml")
    try:
        build_contents = check_output(['curl' , curl]).decode('utf-8')
    except CalledProcessError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}build.toml{ANSI_CODES[4]} failed to download")
        exit(1)

    try:
        if loads(build_contents)['core']['cpu_flags'] == []:
            pass
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: checking if your cpu has neccesary instruction sets")            
            for i in loads(build_contents)['core']['cpu_flags']:
                if i in cpu_flags:
                    continue
                else:
                    print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {i} not in cpu flags")
                    exit(1)
					
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: preparing source for {loads(build_contents)['core']['name']}@{loads(build_contents)['core']['version']}")
        system('git clone '+loads(build_contents)['core']['source']+f" {loads(build_contents)['core']['name']}")
        if loads(build_contents)['core']['depends'] == []:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {pname} has no dependencies so installing it")
            pass
        else:
            for i in loads(build_contents)['core']['depends']:
                print(f"{ANSI_CODES[2]}info{ANSI_CODES[4]}: installing dependency {i} for {pname}")
                install_packages(i)
                
        if preserve_build_files == False:
            environ['NEMESIS_PKG_BUILD_DIR'] = f"/tmp/nemesis-pkg-build/{loads(build_contents)['core']['name']}/{loads(build_contents)['core']['name']}"
        else:
            environ['NEMESIS_PKG_BUILD_DIR'] = f"/var/cache/nemesis-pkg/{loads(build_contents)['core']['name']}/{loads(build_contents)['core']['name']}"
        print(f"{ANSI_CODES[2]}info{ANSI_CODES[4]}: installing {pname}")
        if system(loads(build_contents)['build']['command']) == 0:
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} PASS {pname} installed sucesfully")
            print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: {loads(build_contents)['core']['name']} installed sucessfully")
            if isfile("/etc/nemesis-pkg/installed-packages.PKGLIST") == True:
                installed_pkgs = open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'a+')
                installed_pkgs.seek(0)
                installed_pkgs.write(loads(build_contents)['core']['name']+" "+loads(build_contents)['core']['version']+" "+str(loads(build_contents)['core']['depends'])+" "+str(loads(build_contents)['build']['files'])+"\n")
                installed_pkgs.truncate()
                installed_pkgs.close()
            else:
                installed_pkgs = open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'w', encoding="utf-8")
                installed_pkgs.write(loads(build_contents)['core']['name']+" "+loads(build_contents)['core']['version']+" "+str(loads(build_contents)['core']['depends'])+" "+str(loads(build_contents)['build']['files'])+"\n")
                installed_pkgs.close()
        else:
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} ERROR {pname} failed to install")
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {loads(build_contents)['core']['name']} installed unsucessfully")
                
    except (TOMLDecodeError, KeyError):
        ctime = strftime("%D %H:%M:%S")
        write_log(f"{ctime} ERROR {pname} failed to install")
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: either this package is missing or the build file is corrupt... please open a bug report to the NemesisOS Developers regarding this issue.")

def list_installed():
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: this is the list of all installed packages")
    try:
        ipkglist_open = open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'r', encoding="utf-8")
        a = []
        for installed_pkgs in ipkglist_open.read().splitlines():
            a.append(installed_pkgs.split()[0]+f" {ANSI_CODES[1]}{i.split()[1]}{ANSI_CODES[4]}")

        a.sort()
        for installed_pkgs in a:
            print(i)
            
        ipkglist_open.close()
    except Exception:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: something went wrong")

def list_repos():
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: the available repositories are:")
    for i in REPOLIST:
        print(i[2])

def list_pkgs_from_repo(rname: str):
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: checking if {rname} is a valid repository")
    rexists = False
    rpofile = ""
    for i in REPOLIST:
        if rname not in i:
            continue
        else:
            rexists = True
            rpofile = "/etc/nemesis-pkg/"+i[1]
            break
    
    if rexists == False:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {rname} is not a valid repository.")
    else:
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: showing the list of packages present in {rname}")
        rpofile_open = open(rpofile , 'r')
        for i in rpofile_open.read().splitlines():
            print(i.split()[0], f"{ANSI_CODES[2]}{i.split()[1]}{ANSI_CODES[4]}")

def uninstall_package(pname: str):
    if check_user_is_root() == True:
        pass
    else:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        exit(0)
        
    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: checking if {pname} is a valid package")
    try:
        system("cp /etc/nemesis-pkg/installed-packages.PKGLIST /etc/nemesis-pkg/installed-packages.PKGLIST.bak")
        installed_pkgs = open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'r+')
        pass
    except FileNotFoundError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: the database storing the list of installed packages is not found")
        exit(1)

    installed_packages_db = installed_pkgs.read().splitlines()
    pfound = False
    dlist = []
    pkg_flist = ""
    for i in installed_packages_db:
        if i == "":
            continue
        elif pname == i.split()[0]:
            pfound = True
            pkg_flist = i.split()[3]
        elif pname in literal_eval(i.split()[2]):
            dlist.append(i.split()[0])
        else:
            continue

    if pfound == True and dlist == []:
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: removing {pname}")
        pass
    elif dlist != []:
        print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: removing {pname} will remove the following packages:")
        for i in dlist:
            print(i)
        input_yn = input(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: removing {pname} will remove these packages... do you want to remove them?[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}n{ANSI_CODES[4]}] ")
        if input_yn in ("n", "N"):
            installed_pkgs.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {pname} not removed")
            exit()
        else:
            for i in dlist:
                print(f"{ANSI_CODES[2]}info{ANSI_CODES[4]}: uninstalling {i}")
                uninstall_package(i)
    else:
        installed_pkgs.close()
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {pname} not installed")
        exit(1)

    pkg_flist = literal_eval(pkg_flist)
    for filelist in pkg_flist:
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: removing {i} from filesystem..")
        if i[len(i)-1] != "/":
            if system(f"rm {i}") == 0:
                continue
            else:
                installed_pkgs.close()
                print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {pname} not uninstalled")
                break
        else:
            if system(f"rm -rf {i}") == 0:
                continue
            else:
                installed_pkgs.close()
                print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {pname} not uninstalled")
                break

    print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: {pname} uninstalled..")

    installed_pkg_bak = open("/etc/nemesis-pkg/installed-packages.PKGLIST.bak", 'r')
    ipkglist = ""
    for i in installed_pkg_bak.read().splitlines():
        if i == '':
            continue
        elif i.split()[0] == pname:
            continue
        else:
            ipkglist=ipkglist+f"{i}\n"
            
    installed_pkgs.seek(0)
    installed_pkgs.write(ipkglist)
    installed_pkgs.truncate()
    installed_pkgs.close()
    installed_pkg_bak.close()

def uninstall_multiple(plist: list[str]):
    for i in plist:
        print(f"{ANSI_CODES[2]}note{ANSI_CODES[4]}: removing {i}")
        uninstall_package(i)

def return_if_pkg_exist(query: str):
    try:
        pkglist = open("/etc/nemesis-pkg/installed-packages.PKGLIST" , 'r')
        for i in pkglist.read().splitlines():
            if i.split()[0] == query:
                pkglist.close()
                return True
            else:
                continue

            pkglist.close()
    except (FileNotFoundError, IndexError):
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}/etc/nemesis-pkg/installed-packages.PKGLIST{ANSI_CODES[4]} might be corrupt.. ")

VERSION = 0.1
BUILD_ID = "-rc1"

if __name__ == "__main__":
    parse_config_file()
    try:
        if len(argv) >= 2 and argv[1] == "sync":
            sync_packages(REPOLIST)
        elif len(argv) >= 2 and argv[1] == "version" or argv[1] == "-v":
            print(f"nemesis-pkg build {VERSION}{BUILD_ID}")
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
            if len(argv) == 3 and argv[2] == "installed":
                list_installed()
            elif len(argv) == 3 and argv[2] == "repos":
                list_repos()
            elif len(argv) == 3 and argv[2] == "help":
                print('list: this allows you to list packages/repos\n============================================\ninstalled: shows the installed packages and their versions\nrepos: shows the list of repositories\nrepo_name: shows the list of packages in repo_name\ndefault: shows the list of all packages in every repo')
            elif len(argv) == 3 and argv[2] == "default":
                list_packages()
            elif len(argv) == 3:
                list_pkgs_from_repo(argv[2])
            else:
                list_packages()
        elif len(argv) >=2 and argv[1] == "install":
            if len(argv) == 3:
                install_packages(argv[2])
            else:
                a = []
                for i in range(2, len(argv)):a.append(argv[i])
                install_multiple_packages(a)
        elif len(argv) >= 2 and argv[1] == "uninstall":
            if len(argv) == 3:
                uninstall_package(argv[2])
            else:
                a = []
                for i in range(2 , len(argv)):
                    a.append(argv[i])
                uninstall_multiple(a)
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")

    except IndexError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")
    except KeyboardInterrupt:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user pressed CTRL+C so exiting")
        exit(1)

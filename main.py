#/usr/bin/python3
'''
nemesis-pkg: a tiny and simple package manager for NemesisOS
'''

from os import mkdir, getenv
from os.path import isfile, isdir
from subprocess import check_output
from sys import argv, stdout, exit # pylint: disable=redefined-builtin
from requests import get
from requests.exceptions import MissingSchema, ConnectTimeout
from toml import loads
from toml.decoder import TomlDecodeError

repos = ['https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST'] # pylint: disable=line-too-long
ACCEPT_NONFREE = False # proprietary programs wont be installed by default
DISABLE_HASHCHECK = False # hash checking will be enabled by default
USE_CACHE = True # by default enable caching into /var/nemesis-pkg/$pkg-$ver
colors = stdout.isatty() # use colors only if it is a tty or not

def parse_config():
    ''' 
    parse_config() -> retrive npkg config
    '''
    global colors, ACCEPT_NONFREE, DISABLE_HASHCHECK # pylint: disable=global-statement
    try:
        with open("/etc/nemesis-pkg.conf", 'r', encoding='utf-8') as npkg_config:
            config = loads(npkg_config.read())

            if "colors" in list(config.keys()):
                if config["colors"] is True and colors is True:
                    pass
                else:
                    colors = False

            if "accept_nonfree" in list(config.keys()):
                if config["accept_nonfree"] is True or config["accept_nonfree"] is False:
                    ACCEPT_NONFREE = config["accept_nonfree"]
        npkg_config.close()

        # RETRIEVE FROM ENV VARS ALSO..
        # NPKG_ACCEPT_NONFREE -> 0/1
        # NPKG_USE_COLORS -> 0/1
        # NPKG_DISABLE_HASHCHECKS -> 0/1
        # NPKG_USE_CACHE -> 0/1

        if getenv("NPKG_ACCEPT_NONFREE") is not None and getenv("NPKG_ACCEPT_NONFREE") == 1:
            ACCEPT_NONFREE = True

        # colors are enabled by default anyways
        if getenv("NPKG_USE_COLORS") is not None and int(getenv("NPKG_USE_COLORS")) == 0 and colors:
            colors = False

        # hash verification is enabled so this setting can disable it
        if getenv("NPKG_DISABLE_HASHCHECKS") is not None and int(getenv("NPKG_DISABLE_HASHCHECKS")) == 1: # pylint: disable=line-too-long
            DISABLE_HASHCHECK = True

    except (FileNotFoundError, TomlDecodeError):
        if colors is True:
            print("=> \x1b[33;1mwarning:\x1b[0m using fallback config as config not found or your config is invalid") # pylint: disable=line-too-long
        else:
            print("=> warning: using fallback config as config not found or your config is invalid")

parse_config()

def get_file_from_url(url: str):
    '''
    get_file_from_url("https://random.com/rando.zip") -> rando.zip

    It just returns what file it is downloading
    '''

    return url.split("/")[len(url.split("/"))-1]

def get_fname(file: str):
    '''
    get_fname("sample.zip") -> sample

    It just returns the file name.. not the extension
    '''

    return file.split(".")[0]

def is_root():
    '''
    is_root() -> True/False

    Check whether user is root or not
    '''
    if getenv("USER") == "root":
        return True

    return False

def get_256sum(file: str): # pylint: disable=inconsistent-return-statements
    '''
    get_256sum(file) -> returns the hash of the file
    '''

    if isfile(file):
        return check_output(['sha256sum', file]).decode('utf-8').split()[0]

def update_database(): # pylint: disable=inconsistent-return-statements
    '''
    update_database(): updates repositories database of nemesis-pkg
    '''

    # use repositories locally
    for i in repos:
        name = get_fname(get_file_from_url(i))
        if colors:
            print(f"=> \x1b[34;1minfo:\x1b[0m downloading database for repo \x1b[33;1m{name}\x1b[0m") # pylint: disable=line-too-long
        else:
            print(f"=> info: downloading database for repo {name}")
        try:
            contents = get(i, timeout=60).content.decode('utf-8')

            if isdir("/etc/nemesis-pkg") is False:
                mkdir("/etc/nemesis-pkg")

            with open(f"/etc/nemesis-pkg/{name}.PKGLIST", 'w', encoding="utf-8") as repo_file: # pylint: disable=redefined-outer-name
                repo_file.write(contents)
            repo_file.close()

            if colors:
                print(f"=> \x1b[32;1msuccess:\x1b[0m database for repo \x1b[33;1m{name}\x1b[0m is upto date") # pylint: disable=line-too-long
            else:
                print(f"=> success: database for repo {name} is upto date")

        except (MissingSchema, ConnectTimeout, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError, ConnectionError): # pylint: disable=line-too-long
            if colors:
                print(f"=> \x1b[31;1merror:\x1b[0m downloading database for repo \x1b[33;1m{name}\x1b[0m failed") # pylint: disable=line-too-long
            else:
                print(f"=> error: downloading database for repo {name} failed")
            return 1

def search_package(query: str): # pylint: disable=too-many-branches
    '''
    search_package()
    '''

    for file in repos:
        try:
            arr = {}
            with open(f"/etc/nemesis-pkg/{get_file_from_url(file)}", 'r', encoding="utf-8") as pkglist: # pylint: disable=line-too-long
                db_contents = loads(pkglist.read())
                for pkg in list(sorted(list(db_contents.keys()))):
                    chars = []
                    for i in pkg:
                        if i in list(query) and i not in chars:
                            chars.append(i)

                    if len(chars) == len(query):
                        arr[pkg] = [get_fname(get_file_from_url(file)),
                                    db_contents[pkg]['version'],
                                    db_contents[pkg]['description']]

                pkglist.close()

            for i in list(arr.keys()):
                old_str = ""
                char = []
                if colors:
                    for j in i:
                        if j in list(query) and j not in char:
                            old_str = old_str+f"\x1b[31;1m{j}\x1b[0m"
                            char.append(j)
                        else:
                            old_str = old_str+j

                    if query not in i:
                        if is_package_installed(i.split()[0]):
                            print(f"\x1b[33;1m{arr[i][0]}\x1b[0m/{old_str} \x1b[32;1m{arr[i][1]}\x1b[0m \x1b[34;1m[installed]\x1b[0m") # pylint: disable=line-too-long
                        else:
                            print(f"\x1b[33;1m{arr[i][0]}\x1b[0m/\x1b[0m{old_str} \x1b[32;1m{arr[i][1]}\x1b[0m")
                    else:
                        new = f"\x1b[31;1m{query}\x1b[0m"
                        if is_package_installed(i):
                            print(f"\x1b[33;1m{arr[i][0]}\x1b[0m/{i.replace(query, new)} \x1b[32;1m{arr[i][1]}\x1b[0m \x1b[34;1m[installed]\x1b[0m") # pylint: disable=line-too-long
                        else:
                            print(f"\x1b[33;1m{arr[i][0]}\x1b[0m/{i.split()[0].replace(query, new)} \x1b[32;1m{arr[i][1]}\x1b[0m") # pylint: disable=line-too-long
                else:
                    if is_package_installed(i):
                        print(f"{arr[i][0]}/{i} {arr[i][1]} [installed]")
                    else:
                        print(f"{arr[i][0]}/{i} {arr[i][1]}")

                print(f"└─ {arr[i][2]}")
        except FileNotFoundError:
            if colors:
                print(f"=> \x1b[33;1mwarning:\x1b[0m database for repo \x1b[34;1m{get_fname(get_file_from_url(file))}\x1b[0m not found so skipping.") # pylint: disable=line-too-long
            else:
                print(f"=> warning: database for repo {get_fname(get_file_from_url(file))} not found so skipping.") # pylint: disable=line-too-long
            continue

def is_package_installed(pkg: str):
    '''
    is_package_installed(pkg) -> True/False

    If package is installed then return True otherwise False
    '''

    try:
        with open("/etc/nemesis-pkg/installed-packages.toml", 'r', encoding='utf-8') as ipkg:
            if pkg in list(loads(ipkg.read()).keys()): # package has been found
                ipkg.close()
                return True
        ipkg.close()
    except FileNotFoundError:
        pass

    return False # package has not been found

def install_package(pkgname: str, version: str, hash_check: bool, use_cache: bool, verbose: bool):
    '''
    install_package(pkgname, current, True, True)
    '''
    if is_package_installed(pkgname):
        print("=> note: lul is reinstalled")

    # check package is present in which repo
    pkg_is_in = {}
    main_repo = ""
    for i in repos:
        try:
            with open(f"/etc/nemesis-pkg/{get_file_from_url(i)}", 'r', encoding="utf-8") as repo_db:
                if pkgname in list(loads(repo_db.read()).keys()):
                    pkg_is_in[get_fname(get_file_from_url(i))] = i # take repo name

            repo_db.close()
        except FileNotFoundError:
            continue

    if pkg_is_in == {}:
        if colors:
            print(f"=> \x1b[31;1merror: \x1b[33;1m{pkgname}\x1b[0m is not found in any repos")
        else:
            print(f"=> error: {pkgname} is not found in any repos")
            
        return 1

    if len(list(pkg_is_in.keys())) > 1:
        
        if colors:
            print(f"=> \x1b[34;1mnote: \x1b[33;1m{pkgname}\x1b[0m found in multiple repos:")
        else:
            print(f"=> note: {pkgname} found in multiple repos:")

        for i in list(pkg_is_in.keys()):
            print(f' -> {i}')

        rentered = False
        
        while True:
            if colors:
                if rentered:
                    main_repo = input(f"=> \x1b[33;1mwarning:\x1b[0m repo \x1b[33;1m{main_repo}\x1b[0m not enabled so enter any enabled repo: ")
                else:
                    main_repo = input("=> \x1b[35;1minput:\x1b[0m enter repo: ")
            else:
                main_repo = input("=> input: enter repo: ")

            if main_repo in list(pkg_is_in.keys()):
                break
            else:
                rentered = True
                
    else:
        main_repo = list(pkg_is_in.keys())[0]
    
if __name__ == "__main__":
    try:
        if len(argv) >= 2:
            match argv[1]:
                case "-h" | "--help" | "help" | "h" | "[h]elp":
                    if colors:
                        print('''nemesis-pkg: software package manager
ACTIONS nemesis-pkg {h|i|l|s|u|U|v} [...]
                    
  [\x1b[31;1mh\x1b[0m]\x1b[1melp\x1b[0m\tshow this help message
  [\x1b[31;1mi\x1b[0m]\x1b[1mnstall\x1b[0m\tinstall the given package
  [\x1b[31;1ml\x1b[0m]\x1b[1mist\x1b[0m\tlist all installed packages
  [\x1b[31;1ms\x1b[0m]\x1b[1mearch\x1b[0m\tsearch for the given package
  [\x1b[31;1mu\x1b[0m]\x1b[1mpdate\x1b[0m\tupdate the package database
  [\x1b[31;1mU\x1b[0m]\x1b[1mpgrade\x1b[0m\tupgrade all installed packages
  [\x1b[31;1mv\x1b[0m]\x1b[1mersion\x1b[0m\tprint the program version
                        ''')
                    else:
                        print('''nemesis-pkg: software package manager
ACTIONS nemesis-pkg {h|i|l|s|u|U|v} [...]
                    
  [h]elp\tshow this help messageOA
  [i]nstall\x1b[0m\tinstall the given package
  [l]mist\x1b[0m\tlist all installed packages
  [s]earch\x1b[0m\tsearch for the given package
  [u]pdate\x1b[0m\tupdate the package database
  [U]pgrade\x1b[0m\tupgrade all installed packages
  [v]ersion\x1b[0m\tprint the program version
                        ''')

                case "-v" | "--version" | "version" | "v" | "[v]ersion":
                    print("nemesis-pkg 0.1")
                case "-u" | "update" | "--update" | "u" | "[u]pdate":
                    if is_root():
                        update_database()
                    else:
                        if colors:
                            print("=> \x1b[31;1merror:\x1b[0m \x1b[33;1update\x1b[0m needs to be run as superuser") # pylint: disable=line-too-long
                        else:
                            print("=> errors: update needs to be run as superuser")
                case "-s" | "search" | "--search" | "s" | "[s]earch":
                    if len(argv) >= 3:
                        search_package(argv[2])
                    else:
                        if colors:
                            print("=> \x1b[34;1musage:\x1b[0m nemesis-pkg search \x1b[33;1mpackage\x1b[0m") # pylint: disable=line-too-long
                            print("=> \x1b[31;1merror:\x1b[0m expected \x1b[33;1m1\x1b[0m argument, got \x1b[33;1m0\x1b[0m") # pylint: disable=line-too-long
                        else:
                            print("=> usage: nemesis-pkg search package")
                            print("=> error: expected 1 argument, got 0")

                case "l" | "list" | "--list" | "-l" | "[l]ist":
                    try:
                        with open("/etc/nemesis-pkg/installed-packages.toml", encoding="utf-8") as ipkgdb: # pylint: disable=line-too-long
                            file_contents = loads(ipkgdb.read())
                            for installed in file_contents:
                                if colors:
                                    print(f'{installed} \x1b[32;1m{file_contents[installed]["version"]}\x1b[0m') # pylint: disable=line-too-long
                                else:
                                    print(f'{installed} {file_contents[installed]["version"]}') # pylint: disable=line-too-long
                        ipkgdb.close()
                    except FileNotFoundError:
                        if colors:
                            print("=> \x1b[31;1merror\x1b[0m: \x1b[33;1minstalled-packages.toml:\x1b[0m no such file or directory") # pylint: disable=line-too-long
                        else:
                            print("=> error: installed-packages.toml: no such file or directory")
                case "i" | "install" | "-i" | "--install" | "[i]nstall":
                    verbose_on = False
                    if "--verbose" in argv or "-v" in argv:
                        verbose_on = True
                    
                    install_package("neofetch","current", True, False, False)
                case _:
                    if colors:
                        print("=> \x1b[31;1merror:\x1b[0m invalid choice")
                    else:
                        print("=> error: invalid choice")

                    exit(1)
        else:
            if colors:
                print("=> \x1b[31;1merror:\x1b[0m nemesis-pkg recieved no arguments")
            else:
                print("=> error: nemesis-pkg recieved no arguments")

            exit(1)
    except KeyboardInterrupt:
        if colors:
            print("=> \x1b[31;1merror:\x1b[0m \x1b[33;1mControl-C\x1b[0m pressed so exiting")
        else:
            print("=> error: Control-C pressed so exiting")

        exit(1)

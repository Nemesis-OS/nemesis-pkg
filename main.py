#/usr/bin/python3
'''
nemesis-pkg: a tiny and simple package manager for NemesisOS
'''

from toml import loads, dumps
from toml.decoder import TomlDecodeError
from os import mkdir, getenv
from os.path import isfile, isdir
from subprocess import check_output, CalledProcessError
from sys import argv, exit, stdout
from requests import get
from requests.exceptions import MissingSchema, ConnectionError, ConnectTimeout

repos = ['https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST', 'https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/security.PKGLIST']
accept_nonfree = False # proprietary programs wont be installed
colors = stdout.isatty()

def parse_config():
    '''
    parse_config() -> retrive npkg config
    '''
    global colors
    try:
        with open("/etc/nemesis-pkg.conf", 'r') as npkg_config:
            config = loads(npkg_config.read())

            if "colors" in list(config.keys()):
                if config["colors"] == True and colors == True:
                    pass
                else:
                    colors = False
            
    except (FileNotFoundError, TomlDecodeError):
        if colors == True:
            print("=> \x1b[33;1mwarning:\x1b[0m using fallback config as config not found or your config is invalid")
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

def get_256sum(file: str):
    '''
    get_256sum(file) -> returns the hash of the file
    '''

    if isfile(file) == True:
        return check_output(['sha256sum', file]).decode('utf-8').split()[0]
    else:
        raise FileNotFoundError

def update_database():
    '''
    update_database(): updates repositories database of nemesis-pkg
    '''

    # use repositories locally
    for i in repos:
        name = get_fname(get_file_from_url(i))
        if colors == True:
            print(f"=> \x1b[34;1minfo:\x1b[0m downloading database for repo \x1b[33;1m{name}\x1b[0m")
        else:
            print(f"=> info: downloading database for repo {name}")
        try:
            contents = get(i).content.decode('utf-8')

            if isdir("/etc/nemesis-pkg") == False:
                mkdir("/etc/nemesis-pkg")
                
            with open(f"/etc/nemesis-pkg/{name}.PKGLIST", 'w') as db:
                db.write(contents)
            db.close()

            if colors:
                print(f"=> \x1b[32;1msuccess:\x1b[0m database for repo \x1b[33;1m{name}\x1b[0m is upto date")
            else:
                print(f"=> success: database for repo {name} is upto date")

        except (MissingSchema, ConnectTimeout, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError, ConnectionError):
            if color:
                print(f"=> \x1b[31;1merror:\x1b[0m downloading database for repo \x1b[33;1m{name}\x1b[0m failed")
            else:
                print(f"=> error: downloading database for repo {name} failed")
            return 1

def search_package(query: str):
    '''
    search_package()
    '''

    for file in repos:
        try:
            arr = {}
            with open(f"/etc/nemesis-pkg/{get_file_from_url(file)}", 'r') as db:
                for pkg in db.read().splitlines():
                    str = list(pkg.split()[0])
                    chars = []
                    for i in pkg.split()[0]:
                        if i in list(query) and i not in chars:
                            chars.append(i)

                    if len(chars) == len(query):
                        arr[pkg] = get_fname(get_file_from_url(file))
            db.close()

            for i in arr:
                old_str = ""
                char = []
                
                if colors == True:
                    for j in i.split()[0]:
                        if j in list(query) and j not in char:
                            old_str = old_str+f"\x1b[31;1m{j}\x1b[0m"
                            char.append(j)
                        else:
                            old_str = old_str+j

                    if query not in i.split()[0]:
                        if is_package_installed(i.split()[0]):
                            print(f"{old_str} \x1b[32;1m{i.split()[1]}\x1b[0m \x1b[34;1m[installed]\x1b[0m")
                        else:
                            print(f"{old_str} \x1b[32;1m{i.split()[1]}\x1b[0m")
                    else:
                        nq = f"\x1b[31;1m{query}\x1b[0m"
                        print(f"{i.split()[0].replace(query, nq)} \x1b[32;1m{i.split()[1]}\x1b[0m")
                else:
                    print(i)
        except FileNotFoundError:
            if colors == True:
                print(f"=> \x1b[33;1mwarning:\x1b[0m database for repo \x1b[34;1m{get_fname(get_file_from_url(file))}\x1b[0m not found so skipping.")
            else:
                print(f"=> warning: database for repo {get_fname(get_file_from_url(file))} not found so skipping.")
            continue

def is_package_installed(pkg: str):
    '''
    is_package_installed(pkg) -> True/False

    If package is installed then return True otherwise False
    '''

    try:
        with open("/etc/nemesis-pkg/installed-packages.toml", 'r') as ipkg:
            if pkg in list(loads(ipkg.read()).keys()): # package has been found
                ipkg.close()
                return True
        ipkg.close()
    except FileNotFoundError:
        pass
    
    return False # package has not been found

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
                    
  [h]elp\tshow this help message
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
                            print("=> \x1b[31;1merror:\x1b[0m \x1b[33;1msync\x1b[0m needs to be run as superuser")
                        else:
                            print("=> errors: sync needs to be run as superuser")
                case "-s" | "search" | "--search" | "s" | "[s]earch":
                    if len(argv) >= 3:
                        search_package(argv[2])
                    else:
                        if colors:
                            print("=> \x1b[34;1musage:\x1b[0m nemesis-pkg search \x1b[33;1mpackage\x1b[0m")
                            print("=> \x1b[31;1merror:\x1b[0m expected \x1b[33;1m1\x1b[0m argument, got \x1b[33;1m0\x1b[0m")
                        else:
                            print("=> usage: nemesis-pkg search package")
                            print("=> error: expected 1 argument, got 0")
                            
                case "l" | "list" | "--list" | "-l" | "[l]ist":
                    try:
                        with open(f"/etc/nemesis-pkg/installed-packages.toml") as db:
                            contents = loads(db.read())
                            for i in contents:
                                if colors:
                                    print(f'{i} \x1b[32;1m{contents[i]["version"]}\x1b[0m')
                                else:
                                    print(f'{i} {contents[i]["version"]}')
                        db.close()
                    except FileNotFoundError:
                        if colors:
                            print("=> \x1b[31;1merror\x1b[0m: \x1b[33;1minstalled-packages.toml:\x1b[0m no such file or directory")
                        else:
                            print("=> error: installed-packages.toml: no such file or directory")
                case _:
                    if colors:
                        print("=> \x1b[31;1merror:\x1b[0m invalid choice")
                    else:
                        print("=> error: invalid choice")
        else:
            if colors:
                print("=> \x1b[31;1merror:\x1b[0m nemesis-pkg recieved no arguments")
            else:
                print("=> error: nemesis-pkg recieved no arguments")
    except KeyboardInterrupt:
        if colors:
            print("=> \x1b[31;1merror:\x1b[0m \x1b[33;1mControl-C\x1b[0m pressed so exiting")
        else:
            print("=> error: Control-C pressed so exiting")
            
        exit(1)

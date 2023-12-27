#/usr/bin/python3
'''
nemesis-pkg: a tiny and simple package manager for NemesisOS
'''

from toml import loads, dumps
from os import mkdir, getenv
from os.path import isfile, isdir
from sys import argv, exit
from requests import get
from requests.exceptions import MissingSchema, ConnectionError, ConnectTimeout

repos = ['https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST', 'https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/security.PKGLIST']

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

def use_config():
    '''
    use_config(): this function retrieves config otherwise fallback is used
    '''
    global repos
    if isfile("/etc/nemesis-pkg.conf"):
        try:
            with open("/etc/nemesis-pkg.conf") as a:
                config = a.read()
                config = loads(config)

                if "repos" in list(config.keys()):
                    repos = config["repos"]

            a.close()
        except KeyError:
            print("=> CONFIG ERROR:")
    else:
        print("=> \x1b[33;1mwarning:\x1b[0m using fallback config")

def update_database():
    '''
    update_database(): updates repositories database of nemesis-pkg
    '''

    # use repositories locally
    for i in repos:
        name = get_fname(get_file_from_url(i))
        print(f"=> \x1b[34;1minfo:\x1b[0m downloading database for repo \x1b[33;1m{name}\x1b[0m")
        try:
            contents = get(i).content.decode('utf-8')

            if isdir("/etc/nemesis-pkg") == False:
                mkdir("/etc/nemesis-pkg")
                
            with open(f"/etc/nemesis-pkg/{name}.PKGLIST", 'w') as db:
                db.write(contents)
            db.close()
            print(f"=> \x1b[32;1msucess:\x1b[0m database fore repo \x1b[33;1m{name}\x1b[0m is upto date")

        except (MissingSchema, ConnectTimeout, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError, ConnectionError):
            print(f"=> \x1b[31;1merror:\x1b[0m downloading database for repo \x1b[33;1m{name}\x1b[0m failed")
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
                for j in i.split()[0]:
                    if j in list(query) and j not in char:
                        old_str = old_str+f"\x1b[31;1m{j}\x1b[0m"
                        char.append(j)
                    else:
                        old_str = old_str+j

                print(f"\x1b[35;1m{arr[i]}\x1b[0m/{old_str} \x1b[32;1m{i.split()[1]}\x1b[0m")
                
        except FileNotFoundError:
            print(f"=> \x1b[33;1mwarning:\x1b[0m database for repo \x1b[34;1m{get_fname(get_file_from_url(file))}\x1b[0m not found so skipping.")
            continue
        
if __name__ == "__main__":
    try:
        if len(argv) >= 2:
            match argv[1]:
                case "-h" | "--help" | "help" | "h" | "[h]elp":
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
                case "-v" | "--version" | "version" | "v" | "[v]ersion":
                    print("nemesis-pkg 0.1")
                case "-u" | "update" | "--update" | "u" | "[u]pdate":
                    if is_root():
                        update_database()
                    else:
                        print("=> \x1b[31;1merror:\x1b[0m \x1b[33;1msync\x1b[0m needs to be run as superuser")
                case "-s" | "search" | "--search" | "s" | "[s]earch":
                    if len(argv) >= 3:
                        search_package(argv[2])
                    else:
                        print("=> \x1b[34;1musage:\x1b[0m nemesis-pkg search \x1b[33;1mpackage\x1b[0m")
                        print("=> \x1b[31;1merror:\x1b[0m expected \x1b[33;1m1\x1b[0m argument, got \x1b[33;1m0\x1b[0m")
                case "l" | "list" | "--list" | "-l" | "[l]ist":
                    for i in repos:
                        try:
                            with open(f"/etc/nemesis-pkg/{get_file_from_url(i)}") as db:
                                for j in db.read().splitlines():
                                    print(j)
                            db.close()
                        except FileNotFoundError:
                            continue
                case _:
                    print("=> \x1b[31;1merror:\x1b[0m invalid choice")
        else:
            print("=> \x1b[31;1merror:\x1b[0m nemesis-pkg recieved no arguments")
    except KeyboardInterrupt:
        print("=> \x1b[31;1merror:\x1b[0m \x1b[33;1mControl-C\x1b[0m pressed so exiting")
        exit(1)

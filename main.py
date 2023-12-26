#/usr/bin/python3
'''
nemesis-pkg: a tiny and simple package manager for NemesisOS
'''

from toml import loads, dumps
from os import mkdir
from os.path import isfile, isdir
from sys import argv, exit

def use_config():
    '''
    use_config(): this function retrieves config otherwise fallback is used
    '''
    if isfile("/etc/nemesis-pkg.conf"):
        print("yay")
    else:
        print("nay")
        return 1

if __name__ == "__main__":
    if len(argv) == 2:
        match argv[1]:
            case "-h" | "--help" | "help" | "h" | "[h]elp":
                print('''nemesis-pkg help page\x1b[0m:
======================
[\x1b[1m\x1b[31mh\x1b[0m]\x1b[1melp\x1b[0m - show this page
[\x1b[1m\x1b[32mi\x1b[0m]\x1b[1mnstall\x1b[0m - install \x1b[33m<pkg>\x1b[0m
[\x1b[1m\x1b[33ml\x1b[0m]\x1b[1mist\x1b[0m- list packages
[\x1b[1m\x1b[34ms\x1b[0m]\x1b[1mearch\x1b[0m - search \x1b[33m<pkg>\x1b[0m from database
[\x1b[1m\x1b[35mu\x1b[0m]\x1b[1mpdate\x1b[0m - update package database
[\x1b[1m\x1b[36mU\x1b[0m]\x1b[1mpgrade\x1b[0m - upgrade installed packages
[\x1b[1m\x1b[31mv\x1b[0m]\x1b[1mersion\x1b[0m - how nemesis-pkg version''')
            case "-v" | "--version" | "version" | "v":
                print("nemesis-pkg 0.1")
            case _:
                print("==> ERROR: invalid choice")
    else:
        print("==> \x1b[1m\x1b[31mERROR:\x1b[0m nemesis-pkg recieved no arguments")

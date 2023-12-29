#/usr/bin/python
'''
npkg-genconfig: a simple config generator for nemesis-pkg
'''

from os import getenv1
from os.path import isfile
from toml import dumps, loads
from sys import exit

config = {'colors': True,
          'accept_nonfree': False,
          'cflags': "-march=native -O3 -pipe",
          'cxxflags': "-march=native -O3 -pipe",
          'repos': ['https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST']}

def npkg_input(str, choices):
    '''
    npkg_input(str, choices): input(str choices)
    '''
    while True:
        a = input(str)
        if a in choices:
            return a
try:
    if __name__ == "__main__":
        if getenv("USER") != "root":
            print("=> \x1b[31;1merror:\x1b[0m user is not \x1b[33;1mroot\x1b[0m")
            exit(1)

        use_cols = npkg_input("=> \x1b[35;1minput:\x1b[0m use colors for npkg? [\x1b[32;1my\x1b[0m/\x1b[31;1mn\x1b[0m] ", ["y", "n"])
        
        if use_cols == "n":
            config["colors"] = False

        enable_nonfoss = npkg_input("=> \x1b[35;1minput:\x1b[0m unfree software can hinder the user's freedom; permit building unfree packages? [\x1b[32;1my\x1b[0m/\x1b[31;1mn\x1b[0m] ", ["y", "n"])

        if enable_nonfoss == "y":
            config["accept_nonfree"] = True

        with open("/etc/nemesis-pkg.conf", 'w', encoding="utf-8") as npkg_config:
            npkg_config.write(str(dumps(config)))
        npkg_config.close()

        view_cf = npkg_input("=> \x1b[35;1minput:\x1b[0m do you prefer to view or edit the compiler flags for C and C++? [\x1b[31;1m\x1b[0m/\x1b[32;1me\x1b[0m] ", ["v", "e"])
        if view_cf == "v":
            print(f"=> \x1b[34;1minfo:\x1b[0m compiler flags: \x1b[33;1m{config['cflags']}\x1b[0m")
except KeyboardInterrupt:
    print(" => \x1b[31;1merror:\x1b[0m \x1b[33;1mControl-C\x1b[0m pressed so exiting")
    exit(1)

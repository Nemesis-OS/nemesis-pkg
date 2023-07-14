'''
genconfig-npkg: a tool to generate nemesis-pkg config
'''
#!/usr/bin/python3
import sys
from subprocess import check_output
from shutil import copy
from os import chdir, mkdir, getuid
from os.path import isfile, isdir
from json import dumps

ANSI_CODES = ["\x1b[31m", "\x1b[32m", "\x1b[33m" , "\x1b[34m" , "\x1b[0m"]
REPOS = []
CHECK_NECESSARY_FILES = True
PRESERVE_BUILD_FILES = True
CPU_FLAGS = []
'''
This function only generates the config files and everything
'''
try:
    if __name__ == "__main__":
        if getuid() != 0:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
            sys.exit(1)
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: finding if config.json found..")
        if isdir("/etc/nemesis-pkg/") is False:
            print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: /etc/nemesis-pkg not found..")
            mkdir("/etc/nemesis-pkg")
        chdir("/etc/nemesis-pkg/")
        if isfile("config.json") is True:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: saving a copy of your existing config..")
            copy("config.json", "config.json.bak")
        else:
            pass
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: fetching cpu flags.")
        CPU_FLAGS = check_output('lscpu').decode('utf-8').splitlines()
        for i in CPU_FLAGS:
            if i.split()[0] == "Flags:":
                CPU_FLAGS = i.split()
                break
        CPU_FLAGS.pop(0)
        if not CPU_FLAGS:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: cpu flag generation failed")
            sys.exit(1)
        else:
            print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: cpu flags made sucessfully")
            yn = input(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: do you want to view cpu flags?[y/n] ")
            if yn in ("y", "Y"):
                print(CPU_FLAGS)
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: making repos..")
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: release and security repo enabled..")
        REPOS = [
        ["https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST",
         "release.PKGLIST",
         "release",
         "https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/"],
        ["https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/security.PKGLIST",
         "security.PKGLIST",
         "security-updates",
         "https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/"]
        ]
        enable_community = input(f"{ANSI_CODES[3]}input{ANSI_CODES[4]}: enable ncr repo?[y/n] ")
        if enable_community in ("y", "Y"):
            REPOS.append(
                [
                    "https://raw.githubusercontent.com/Nemesis-OS/packages-community/main/community.PKGLIST",  # pylint: disable=line-too-long
                          "community.PKGLIST",
                          "community",
                          "https://raw.githubusercontent.com/Nemesis-OS/packages-community/main/"])
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: repository was configured")
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: generating config file")
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: config generated so saving it")
    with open("config.json", 'w', encoding='utf-8') as cfg_file:
        hmap = {'REPOS': REPOS, 'CPU_FLAGS': CPU_FLAGS, 'SAVE_BUILD_FILES': PRESERVE_BUILD_FILES}
        cfg_file.write(dumps(hmap))
    cfg_file.close()
    print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: config generated sucessfully")
except KeyboardInterrupt:
    print(f" {ANSI_CODES[0]}error{ANSI_CODES[4]}: user pressed ctrl-c so exiting. ")
    sys.exit(1)

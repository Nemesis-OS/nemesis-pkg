#=====================================================
#genconfig-npkg: a tool to generate nemesis-pkg config|
#=====================================================

from subprocess import check_output
from os.path import isfile, isdir
from os import chdir, mkdir, system

ANSI_CODES = ["\x1b[31m", "\x1b[32m", "\x1b[33m" , "\x1b[34m" , "\x1b[0m"]
REPOS = []
check_nessary_files = True
preserve_build_files = True

try:
    if __name__ == "__main__":
        if check_output("whoami") != b'root\n':
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: root user is needed to run this program")
            exit(1)
        else:
            pass
    
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: checking if {ANSI_CODES[2]}/etc/nemesis-pkg/config.py{ANSI_CODES[4]} found..")
        if isdir("/etc/nemesis-pkg/") == True:
            chdir("/etc/nemesis-pkg/")
            pass
        else:
            print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: {ANSI_CODES[3]}/etc/nemesis-pkg{ANSI_CODES[4]} not found..")
            mkdir("/etc/nemesis-pkg")
            pass

        chdir("/etc/nemesis-pkg/")

        if isfile("config.py") == True:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: saving a snapshot of your existing config on {ANSI_CODES[2]}config.py.bak{ANSI_CODES[4]}")
            system("cp config.py config.py.bak")
        else:
            pass

        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: fetching cpu flags.")
        cpu_flags = check_output('lscpu').decode('utf-8').splitlines()[22].split()
        cpu_flags.pop(0)
        
        if cpu_flags == []:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: cpu flags not generated")
            exit(1)
        else:
            print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: cpu flags generated sucessfully")
            yn = input(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: do you want to view cpu flags?[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}n{ANSI_CODES[4]}] ")
            if yn == "y" or yn == "Y":
                print(cpu_flags)
                pass
            else:
                pass

        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: making repositories..")
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: {ANSI_CODES[2]}release{ANSI_CODES[4]} and {ANSI_CODES[2]}security{ANSI_CODES[4]} repository enabled..")
        REPOS = [
        ["https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/release.PKGLIST" , "release.PKGLIST" , "release" , "https://raw.githubusercontent.com/Nemesis-OS/packages-release/main/"],
        ["https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/security.PKGLIST" , "security.PKGLIST" , "security-updates" , "https://raw.githubusercontent.com/Nemesis-OS/packages-security/main/"]
        ]

        enable_community = input(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: would you like to enable {ANSI_CODES[2]}community{ANSI_CODES[4]} repo..[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}n{ANSI_CODES[4]}] ")
        if enable_community == "y" or enable_community == "Y":
            REPOS.append(["https://raw.githubusercontent.com/Nemesis-OS/packages-community/main/community.PKGLIST", "community.PKGLIST", "community", "https://raw.githubusercontent.com/Nemesis-OS/packages-community/main/"])
        else:
            pass

        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: repository were configured")

    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: generating config file")
    config_file = f'''ANSI_CODES = {ANSI_CODES}
REPOS = {REPOS}
cpu_flags = {cpu_flags}
check_necessary_files = {check_nessary_files}
preserve_build_files = {preserve_build_files}'''

    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: config generated so saving it")
    cfg_file = open("config.py", 'w')
    cfg_file.write(config_file)
    cfg_file.close()
    print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: config generated sucessfully")
        
except KeyboardInterrupt:
    print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user pressed ctrl-c so exiting. ")
    exit(1)

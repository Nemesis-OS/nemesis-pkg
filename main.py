#!/usr/bin/python3
"""Main file of Nemesis package manager"""
from os import mkdir, chdir, system, environ
from os.path import isfile
from sys import argv, path
from subprocess import check_output, CalledProcessError
from time import strftime
from tomllib import loads, TOMLDecodeError
from ast import literal_eval
import sys
import config

DISABLE_CHECK_IMPORTANT_FILES = False
PRESERVE_BUILD_FILES = False
ANSI_CODES = []
REPOLIST = []
CPU_FLAGS = []


def check_user_is_root():
    """Check whether user running the program is a root user."""
    cuser = check_output("whoami")
    return cuser == b"root\n"


def parse_config_file():
    """Parse config file of Nemesis package manager"""
    global DISABLE_CHECK_IMPORTANT_FILES, ANSI_CODES, REPOLIST, CPU_FLAGS, PRESERVE_BUILD_FILES
    if not isfile("/etc/nemesis-pkg/config.py"):
        print("error: config file not found")
        sys.exit(1)
    chdir("/etc/nemesis-pkg")
    path.append("/etc/nemesis-pkg")

    if str(type(config.ANSI_CODES)) == "<class 'list'>" and len(config.ANSI_CODES) == 5:
        ANSI_CODES = config.ANSI_CODES
    else:
        print(
            "config error.. ANSI_CODES is either missing or there are less than 5 numbers"
        )

    DISABLE_CHECK_IMPORTANT_FILES = config.CHECK_NECESSARY_FILES

    REPOLIST = config.REPOS

    PRESERVE_BUILD_FILES = config.PRESERVE_BUILD_FILES

    if not config.CPU_FLAGS:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: cpu flags is not defined")
    else:
        CPU_FLAGS = config.CPU_FLAGS


def sync_packages(pkglist: list[list[str]]):
    """Sync packages"""
    if not check_user_is_root():
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: root user can only run update")
        sys.exit(1)

    for pkg in pkglist:
        fexists = False
        print(
            f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: updating {ANSI_CODES[2]}{pkg[1]}{ANSI_CODES[4]}"
        )
        if isfile(f"/etc/nemesis-pkg/{pkg[1]}") is True:
            fexists = True
            plist = open(f"/etc/nemesis-pkg/{pkg[1]}", "r+", encoding="utf-8")
            list_contents = plist.read()
        else:
            print(
                f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: "
                + f"{ANSI_CODES[2]}{pkg[1]}{ANSI_CODES[4]} not found so creating it.."
            )
            plist = open(f"/etc/nemesis-pkg/{pkg[1]}", "w", encoding="utf-8")
        downloaded_version = check_output(["curl", pkg[0]]).decode("utf-8")

        if fexists is False:
            plist.write(str(downloaded_version))
            plist.close()
            print(
                f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: made {ANSI_CODES[2]}{pkg[1]}{ANSI_CODES[4]}"
            )
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} UPDATE {pkg[1]}")
        elif list_contents != str(downloaded_version):
            plist.seek(0)
            plist.write(str(downloaded_version))
            plist.truncate()
            plist.close()
            print(
                f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: "
                + f"{ANSI_CODES[2]}{pkg[1]}{ANSI_CODES[4]} updated.."
            )
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} UPDATE {pkg[1]}")
        else:
            print(
                f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: "
                + f"{ANSI_CODES[2]}{pkg[1]}{ANSI_CODES[4]} was up to date"
            )
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} UPDATE {pkg[1]}")


def write_log(text: str):
    """Write logs to log file"""
    log_exist = isfile("/etc/nemesis-pkg/nemesis-pkg.log")
    if log_exist:
        chdir("/etc/nemesis-pkg")
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log", "r+", encoding="utf-8")
        logfile.seek(0)
        if logfile.read().splitlines == []:
            logfile.write(f"{text}\n")
        else:
            logfile.write(f"{text}\n")
        logfile.truncate()
        logfile.close()
    else:
        chdir("/etc/nemesis-pkg")
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log", "w", encoding="utf-8")
        logfile.write(f"{text}\n")
        logfile.close()


def view_log():
    """View logs from log file"""
    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: viewing the nemesis-pkg log file")
    chdir("/etc/nemesis-pkg")
    try:
        logfile = open("/etc/nemesis-pkg/nemesis-pkg.log", "r", encoding="utf-8")
        print(logfile.read())
        logfile.close()
    except FileNotFoundError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: file not found")


def remove_log():
    """Remove logs from log file"""
    if not check_user_is_root():
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        sys.exit(1)

    yes_or_no = input(
        f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: "
        + "removing the logfile will delete the list of all the operations you executed..."
        + f"[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}N{ANSI_CODES[4]}] "
    )
    if yes_or_no in ["Y", "y"]:
        print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: removing logfile")
        chdir("/etc/nemesis-pkg")
        if system("rm nemesis-pkg.log") == 0:
            print(
                f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: the logfile was removed succesfully"
            )
        else:
            print(
                f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: "
                + "something went wrong that is why the logfile was not removed"
            )
            sys.exit(1)
    else:
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: the logfile was not deleted")


def list_packages():
    """List packages"""
    for repo in REPOLIST:
        file = open(f"/etc/nemesis-pkg/{repo[1]}", "r", encoding="utf-8")
        for pkg in file.read().splitlines():
            print(
                str(
                    f"{ANSI_CODES[2]}{repo[2]}{ANSI_CODES[4]}/{pkg.split()[0]} "
                    + f"{ANSI_CODES[1]}{pkg.split()[1]}{ANSI_CODES[4]}"
                )
            )


def install_multiple_packages(pkglist: list[str]):
    """Install multiple packages"""
    if not check_user_is_root():
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        sys.exit(1)

    for pkg in pkglist:
        install_packages(pkg)


def install_packages(pname: str):
    """Install package"""
    if not check_user_is_root:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        sys.exit(1)

    # pkg_in_repo = False
    # pkg_in_w_repo = False
    # reinstall_mode = False

    if return_if_pkg_exist(pname):
        reinstall_yn = input(
            f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: "
            + f"{ANSI_CODES[2]}{pname}{ANSI_CODES[4]} is installed.. do you wanna reinstall"
            + f"[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}n{ANSI_CODES[4]}] "
        )
        if reinstall_yn in ("n", "N"):
            return None
        else:
            pass

    if PRESERVE_BUILD_FILES is False:
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

    print(
        f"{ANSI_CODES[3]}build{ANSI_CODES[4]}: "
        + f"checking if {ANSI_CODES[2]}{pname}{ANSI_CODES[4]} is in repositories.."
    )
    for repo in REPOLIST:
        current_db = open(f"/etc/nemesis-pkg/{repo[1]}", "r", encoding="utf-8")
        for j in current_db.read().splitlines():
            if j.split()[0] in pname:
                # pkg_in_repo = True
                # pkg_in_w_repo = repo
                curl = f"{repo[3]}{pname}/build"
                current_db.close()
            else:
                # pkg_in_repo = False
                current_db.close()
                continue

        current_db.close()

    if not curl:
        print(
            f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: "
            + f"{ANSI_CODES[2]}{pname}{ANSI_CODES[4]} is not in any repositories"
        )
        sys.exit(1)
    else:
        pass

    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: downloading build.toml")
    try:
        build_contents = check_output(["curl", curl]).decode("utf-8")
    except CalledProcessError:
        print(
            f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: "
            + f"{ANSI_CODES[2]}build.toml{ANSI_CODES[4]} failed to download"
        )
        sys.exit(1)

    try:
        if loads(build_contents)["core"]["CPU_FLAGS"] == []:
            pass
        else:
            print(
                f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: "
                + "checking if your cpu has neccesary instruction sets"
            )
            for cpu_flag in loads(build_contents)["core"]["CPU_FLAGS"]:
                if cpu_flag in CPU_FLAGS:
                    continue
                else:
                    print(
                        f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {cpu_flag} not in cpu flags"
                    )
                    sys.exit(1)

        print(
            f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: preparing source for "
            + f"{loads(build_contents)['core']['name']}@{loads(build_contents)['core']['version']}"
        )
        system(
            "git clone "
            + loads(build_contents)["core"]["source"]
            + f" {loads(build_contents)['core']['name']}"
        )
        if loads(build_contents)["core"]["depends"] == []:
            print(
                f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {pname} has no dependencies so installing it"
            )
        else:
            for dependency in loads(build_contents)["core"]["depends"]:
                print(
                    f"{ANSI_CODES[2]}info{ANSI_CODES[4]}: "
                    + f"installing dependency {dependency} for {pname}"
                )
                install_packages(dependency)

        if not PRESERVE_BUILD_FILES:
            environ["NEMESIS_PKG_BUILD_DIR"] = (
                "/tmp/nemesis-pkg-build/"
                + f"{loads(build_contents)['core']['name']}/{loads(build_contents)['core']['name']}"
            )
        else:
            environ["NEMESIS_PKG_BUILD_DIR"] = (
                "/var/cache/nemesis-pkg/"
                + f"{loads(build_contents)['core']['name']}/{loads(build_contents)['core']['name']}"
            )
        print(f"{ANSI_CODES[2]}info{ANSI_CODES[4]}: installing {pname}")
        if system(loads(build_contents)["build"]["command"]) == 0:
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} PASS {pname} installed sucesfully")
            print(
                f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: "
                + f"{loads(build_contents)['core']['name']} installed sucessfully"
            )
            if isfile("/etc/nemesis-pkg/installed-packages.PKGLIST"):
                installed_pkgs = open(
                    "/etc/nemesis-pkg/installed-packages.PKGLIST",
                    "a+",
                    encoding="utf-8",
                )
                installed_pkgs.seek(0)
                installed_pkgs.write(
                    loads(build_contents)["core"]["name"]
                    + " "
                    + loads(build_contents)["core"]["version"]
                    + " "
                    + str(loads(build_contents)["core"]["depends"])
                    + " "
                    + str(loads(build_contents)["build"]["files"])
                    + "\n"
                )
                installed_pkgs.truncate()
                installed_pkgs.close()
            else:
                installed_pkgs = open(
                    "/etc/nemesis-pkg/installed-packages.PKGLIST", "w", encoding="utf-8"
                )
                installed_pkgs.write(
                    loads(build_contents)["core"]["name"]
                    + " "
                    + loads(build_contents)["core"]["version"]
                    + " "
                    + str(loads(build_contents)["core"]["depends"])
                    + " "
                    + str(loads(build_contents)["build"]["files"])
                    + "\n"
                )
                installed_pkgs.close()
        else:
            ctime = strftime("%D %H:%M:%S")
            write_log(f"{ctime} ERROR {pname} failed to install")
            print(
                f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: "
                + f"{loads(build_contents)['core']['name']} installed unsucessfully"
            )

    except (TOMLDecodeError, KeyError):
        ctime = strftime("%D %H:%M:%S")
        write_log(f"{ctime} ERROR {pname} failed to install")
        print(
            f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: "
            + "either this package is missing or the build file is corrupt... "
            + "please open a bug report to the NemesisOS Developers regarding this issue."
        )


def list_installed():
    """List installed packages"""
    print(
        f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: this is the list of all installed packages"
    )
    try:
        ipkglist_open = open(
            "/etc/nemesis-pkg/installed-packages.PKGLIST", "r", encoding="utf-8"
        )
        packages = []
        for installed_pkgs in ipkglist_open.read().splitlines():
            packages.append(
                installed_pkgs.split()[0]
                + f" {ANSI_CODES[1]}{i.split()[1]}{ANSI_CODES[4]}"
            )

        packages.sort()
        for installed_pkgs in packages:
            print(i)

        ipkglist_open.close()
    except Exception:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: something went wrong")


def list_repos():
    """List repositories"""
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: the available repositories are:")
    for repo in REPOLIST:
        print(repo[2])


def list_pkgs_from_repo(rname: str):
    """List packages from a repository"""
    print(
        f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: checking if {rname} is a valid repository"
    )
    rexists = False
    rpofile = ""
    for repo in REPOLIST:
        if rname in repo:
            rexists = True
            rpofile = "/etc/nemesis-pkg/" + repo[1]
            break

    if not rexists:
        print(
            f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {rname} is not a valid repository."
        )
    else:
        print(
            f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: showing the list of packages present in {rname}"
        )
        rpofile_open = open(rpofile, "r", encoding="utf-8")
        for repo in rpofile_open.read().splitlines():
            print(repo.split()[0], f"{ANSI_CODES[2]}{repo.split()[1]}{ANSI_CODES[4]}")


def uninstall_package(pname: str):
    """Uninstall a package"""
    if not check_user_is_root():
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user is not root")
        sys.exit(0)

    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: checking if {pname} is a valid package")
    try:
        system(
            "cp /etc/nemesis-pkg/installed-packages.PKGLIST "
            + "/etc/nemesis-pkg/installed-packages.PKGLIST.bak"
        )
        installed_pkgs = open(
            "/etc/nemesis-pkg/installed-packages.PKGLIST", "r+", encoding="utf-8"
        )
        pass
    except FileNotFoundError:
        print(
            f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: "
            + "the database storing the list of installed packages is not found"
        )
        sys.exit(1)

    installed_packages_db = installed_pkgs.read().splitlines()
    pfound = False
    dlist = []
    pkg_flist = ""
    for installed_pkg in installed_packages_db:
        if not installed_pkg:
            continue
        elif pname == installed_pkg.split()[0]:
            pfound = True
            pkg_flist = installed_pkg.split()[3]
        elif pname in literal_eval(installed_pkg.split()[2]):
            dlist.append(installed_pkg.split()[0])
        else:
            continue

    if pfound and not dlist:
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: removing {pname}")
    elif dlist:
        print(
            f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: "
            + f"removing {pname} will remove the following packages:"
        )
        for dependency in dlist:
            print(dependency)
        input_yn = input(
            f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: "
            + f"removing {pname} will remove these packages... do you want to remove them?"
            + f"[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}n{ANSI_CODES[4]}] "
        )
        if input_yn in ("n", "N"):
            installed_pkgs.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {pname} not removed")
            sys.exit()
        else:
            for dependency in dlist:
                print(f"{ANSI_CODES[2]}info{ANSI_CODES[4]}: uninstalling {dependency}")
                uninstall_package(dependency)
    else:
        installed_pkgs.close()
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {pname} not installed")
        sys.exit(1)

    pkg_flist = literal_eval(pkg_flist)
    for filelist in pkg_flist:
        print(
            f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: removing {filelist} from filesystem.."
        )
        if filelist[len(filelist) - 1] != "/":
            if system(f"rm {filelist}") == 0:
                continue
            else:
                installed_pkgs.close()
                print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {pname} not uninstalled")
                break
        else:
            if system(f"rm -rf {filelist}") == 0:
                continue
            else:
                installed_pkgs.close()
                print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {pname} not uninstalled")
                break

    print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: {pname} uninstalled..")

    installed_pkg_bak = open(
        "/etc/nemesis-pkg/installed-packages.PKGLIST.bak", "r", encoding="utf-8"
    )
    ipkglist = ""
    for installed_pkg in installed_pkg_bak.read().splitlines():
        if not installed_pkg:
            continue
        elif installed_pkg.split()[0] == pname:
            continue
        else:
            ipkglist = ipkglist + f"{installed_pkg}\n"

    installed_pkgs.seek(0)
    installed_pkgs.write(ipkglist)
    installed_pkgs.truncate()
    installed_pkgs.close()
    installed_pkg_bak.close()


def uninstall_multiple(plist: list[str]):
    """Uninstall multiple packages"""
    for package in plist:
        print(f"{ANSI_CODES[2]}note{ANSI_CODES[4]}: removing {package}")
        uninstall_package(package)


def return_if_pkg_exist(query: str):
    """Returns if pkg exist"""
    try:
        pkglist = open(
            "/etc/nemesis-pkg/installed-packages.PKGLIST", "r", encoding="utf-8"
        )
        for pkg in pkglist.read().splitlines():
            if pkg.split()[0] == query:
                pkglist.close()
                return True

            pkglist.close()
    except (FileNotFoundError, IndexError):
        print(
            f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: {ANSI_CODES[2]}"
            + f"/etc/nemesis-pkg/installed-packages.PKGLIST{ANSI_CODES[4]} might be corrupt.. "
        )


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
                print(
                    "log: this allows you to view/delete logs\n"
                    + "========================================\n"
                    + "view: this allows you to view logfile\n"
                    + "delete: this allows you to delete logfile"
                )
            elif len(argv) == 3 and argv[2] == "view" or argv[2] == "v":
                view_log()
            elif len(argv) == 3 and argv[2] == "delete" or argv[2] == "d":
                remove_log()
            else:
                print(
                    "log: this allows you to view/delete logs\n"
                    + "========================================\n"
                    + "view: this allows you to view logfile\n"
                    + "delete: this allows you to delete logfile"
                )
        elif len(argv) >= 2 and argv[1] == "list":
            if len(argv) == 3 and argv[2] == "installed":
                list_installed()
            elif len(argv) == 3 and argv[2] == "repos":
                list_repos()
            elif len(argv) == 3 and argv[2] == "help":
                print(
                    "list: this allows you to list packages/repos\n"
                    + "============================================\n"
                    + "installed: shows the installed packages and their versions\n"
                    + "repos: shows the list of repositories\n"
                    + "repo_name: shows the list of packages in repo_name\n"
                    + "default: shows the list of all packages in every repo"
                )
            elif len(argv) == 3 and argv[2] == "default":
                list_packages()
            elif len(argv) == 3:
                list_pkgs_from_repo(argv[2])
            else:
                list_packages()
        elif len(argv) >= 2 and argv[1] == "install":
            if len(argv) == 3:
                install_packages(argv[2])
            else:
                a = []
                for i in range(2, len(argv)):
                    a.append(argv[i])
                install_multiple_packages(a)
        elif len(argv) >= 2 and argv[1] == "uninstall":
            if len(argv) == 3:
                uninstall_package(argv[2])
            else:
                a = []
                for i in range(2, len(argv)):
                    a.append(argv[i])
                uninstall_multiple(a)
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")

    except IndexError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")
    except KeyboardInterrupt:
        print(
            f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user pressed CTRL+C so sys.exiting"
        )
        sys.exit(1)

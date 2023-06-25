#!/usr/bin/python3
from os import mkdir, chdir, getlogin, system
from os.path import isdir, isfile
from sys import argv, exit, path
from subprocess import check_output, CalledProcessError
from shutil import copy
from time import strftime

#disable_check_important_files = True
ANSI_CODES = []
REPOLIST = []

def parse_config_file():
    global disable_check_important_files, ANSI_CODES, REPOLIST
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

    if config.check_nessary_files == False:
        disable_check_important_files = False
    else:
        disable_check_important_files = True

    REPOLIST = config.REPOS

def sync_packages(PKGLIST: list[list[str]]):
    #if check_output("whoami") != b'root\n':
        #print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: root user can only run update")
        #exit(1)
    #else:
        #pass
    
    for i in range(0 , len(PKGLIST)):                
        fexists = False
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: updating {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]}")
        if isfile(f"/etc/nemesis-pkg/{PKGLIST[i][1]}") == True:
            fexists = True
            plist = open(f"/etc/nemesis-pkg/{PKGLIST[i][1]}" , 'r+')
            list_contents = plist.read()
            pass
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} not found so creating it..")
            plist = open(f"/etc/nemesis-pkg/{PKGLIST[i][1]}" , 'w')    
        downloaded_version = check_output(['curl' , PKGLIST[i][0]]).decode("utf-8")
        
        if fexists == False:
            plist.write(str(downloaded_version))
            plist.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: made {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]}")
        elif list_contents != str(downloaded_version):
            plist.seek(0)
            plist.write(str(downloaded_version))
            plist.truncate()
            plist.close()
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} updated..")
        else:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{PKGLIST[i][1]}{ANSI_CODES[4]} was up to date")

        ctime = strftime("%D %H:%M:%S")
        write_history(f"{ctime} {ANSI_CODES[2]}{PKGLIST[i][2]}{ANSI_CODES[4]} repo updated..")

    write_hist_snapshot()

def write_history(current_opr: str):
    history_npkg = False
    if isfile(f"/home/{getlogin()}/.nemesis-pkg_history") == True:
        history_npkg = True
        history = open(f"/home/{getlogin()}/.nemesis-pkg_history" , 'r+')
    else:
        history = open(f"/home/{getlogin()}/.nemesis-pkg_history" , 'w')

    if history_npkg == False:
        history.write(current_opr)
        history.close()
    else:
        history.seek(0)
        historyc = history.read()
        historyc = historyc + f"\n{current_opr}"
        history.write(historyc)
        history.truncate()
        history.close()

    copy(f"/home/{getlogin()}/.nemesis-pkg_history" , "/etc/nemesis-pkg/.nemesis-pkg_history")

def delete_history(date: str):
    try:
        hist_file = open(f"/home/{getlogin()}/.nemesis-pkg_history" , 'r+')
    except PermissionError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: you need to be root in order to run this")
        exit(1)

    if date == "all":
        hist_file.seek(0)
        hist_file.truncate()
        hist_file.close()
    else:
        a = []
        history = hist_file.read()
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: deleting {ANSI_CODES[2]}{date}{ANSI_CODES[4]} from history")
        for i in range(0,len(history.splitlines())):
            if history.splitlines()[i].find(date) > -1:
                print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: {ANSI_CODES[2]}{date}{ANSI_CODES[4]} found so deleting it")
            else:
                a.append(history.splitlines()[i])
                continue

        history = ''
        for i in range(0 , len(a)):
            history = history + a[i]
            
        hist_file.seek(0)
        hist_file.write(history)
        hist_file.truncate()
        hist_file.close()

def write_hist_snapshot():
    snapshot_exists = True
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: writing snapshot of the history")
    try:
        chdir("/etc/nemesis-pkg/.history_snapshots")
    except FileNotFoundError:
        snapshot_exists = False
        print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: history snapshots directory not found so creating it..")
        chdir("/etc/nemesis-pkg")
        mkdir("/etc/nemesis-pkg/.history_snapshots")
        pass

    if snapshot_exists == False:
        chdir("/etc/nemesis-pkg/.history_snapshots")
        file_metadata = open("meta" , 'w')
        metanum = 0
        file_metadata.write(str(metanum))
        file_metadata.close()
    else:
        if isfile("meta") == True:
            file_metadata = open("meta" , 'r+')
            metanum = file_metadata.read()
            metanum = int(metanum)+1
            metanum = int(str('0'+str(metanum)))
            file_metadata.seek(0)
            file_metadata.write(str(metanum))
            file_metadata.truncate()
            file_metadata.close()
        #else:
        

    time = strftime("%d_%m_%y")
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: copying history to the snapshots folder")
    copy(f"/etc/nemesis-pkg/.nemesis-pkg_history" , f"{str(metanum)}_{time}_history.bak")
    print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: snapshot of history was taken succesfully")

def delete_snapshot(id: int):
    if id == 0:
        if input(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: this is an irreversible operation and all the saved snapshots will be lost.. do you want to continue it[{ANSI_CODES[1]}y{ANSI_CODES[4]}/{ANSI_CODES[0]}N{ANSI_CODES[4]}] ") == "y":
            chdir("/etc/nemesis-pkg/.history_snapshots")
            # reset meta
            meta = open('meta' , 'r+')
            meta.seek(0)
            meta.write(str(0))
            meta.truncate()
            meta.close()
            if system("rm -rf *.bak") != 0:
                print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: snapshot was not deleted due to some errors")
            else:
                print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: snapshot deleted sucessfully")
        else:
            print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: user decided to cancel")
    else:
        chdir("/etc/nemesis-pkg/.history_snapshots")
        files_exist = check_output('ls').decode('utf-8').split()
        if files_exist == ['meta']:
            print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: no files will be deleted as meta is the only file")
            exit(0)
        else:
            pass
        
        for i in files_exist:
            a = []
            num = ""
            for j in range(0, len(i)):
                if i[j] == "_":
                    break
                else:
                    a.append(i[j])

            print(a)

            if len(a) == 1:
                num = int(a[0])
            else:
                for k in range(0,len(a)):
                    num = num+str(a[k])
                    
            if int(num) == id:
                print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: deleting snapshot with id {id}")
                system(f"rm {i}")
            else:
                continue
            
def overwrite_history(snapshot_id: int):
    print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: resetting nemesis-pkg history to snapshot id {snapshot_id}")
    chdir("/etc/nemesis-pkg/.history_snapshots")
    file_there = check_output('ls').decode('utf-8').split()
    if file_there == ['meta']:
        print(f"{ANSI_CODES[2]}warning{ANSI_CODES[4]}: meta is the only file here so this operation will cancel")
        exit()
    else:
        for i in file_there:
            a = []
            id = ''
            if i == 'meta':
                continue

            for j in range(0 , len(i)):
                if i[j] != "_":
                    a.append(i[j])
                else:
                    break

            for k in a:
                id = str(id+k)

            if int(k) == int(snapshot_id):
                print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: resetting history to snapshot id {snapshot_id}")
                copy(i , "/etc/nemesis-pkg/.nemesis-pkg_history")
                copy(i , f"/home/{getlogin()}/.nemesis-pkg_history")
                break
            else:
                continue

        if id != '':
            print(f"{ANSI_CODES[1]}sucess{ANSI_CODES[4]}: history overwrote to snapshot id {snapshot_id}")
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: history failed to overwrite with snapshot id {snapshot_id}")

def view_history(id: int):
    if id == -1:
        num = 0
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: viewing all the snapshots of history.")
        chdir("/etc/nemesis-pkg/.history_snapshots")
        flist = check_output('ls').decode('utf-8').split()
        for i in flist:
            if i == 'meta':
                break
            else:
                print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: viewing snapshot file with id {num}")
                num = num+1
                sfile = open(i , 'r')
                print(sfile.read())
                sfile.close()
                continue
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: all the history snapshots have been shown")
    else:
        print(f"{ANSI_CODES[3]}note{ANSI_CODES[4]}: viewing snapshot id {id}")
        
                                  
VERSION = 0.1
BUILD_NUM = 23619

if __name__ == "__main__":
    parse_config_file()
    try:
        if len(argv) >= 2 and argv[1] == "sync":
            sync_packages(REPOLIST)
        elif len(argv) >= 2 and argv[1] == "version" or argv[1] == "-v":
            print(f"nemesis-pkg build {VERSION} {BUILD_NUM}")
        elif len(argv) > 2 and argv[1] == "history":
            if argv[2] == "view":
                file = open(f"/home/{getlogin()}/.nemesis-pkg_history")
                print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: this is the complete history of operations run by nemesis-pkg")
                print(file.read())
                file.close()
            elif len(argv) == 4 and argv[2] == "delete":
                delete_history(argv[3])
            elif len(argv) > 3 and argv[2] == "undo" or argv[2] == "redo":
                overwrite_history(argv[3])
            elif len(argv) > 4 and argv[2] == "snapshot":
                if argv[3] == "delete":
                    try:
                        if argv[4] == "all":
                            delete_snapshot(0)
                        else:
                            delete_snapshot(int(argv[4]))
                    except ValueError:
                        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid snapshot id")
                        exit(1)
                elif argv[3] == "view":
                    if argv[4] == "all":
                        view_history(-1)
            elif len(argv) == 3 and argv[2] == "help":
                print("nemesis-pkg history help\n========================\nview: views the history file to see operations run by users\ndelete: this command deletes history from a given date. all keyword clears history\nsnapshot: this command allows to view/delete history snapshots\nundo: undoes history with snapshot id..\nredo: redos history with snapshot id")
        elif len(argv) == 2 and argv[1] == "history":
                file = open(f"/home/{getlogin()}/.nemesis-pkg_history")
                print(f"{ANSI_CODES[3]}info{ANSI_CODES[4]}: this is the complete history of operations run by nemesis-pkg")
                print(file.read())
                file.close()
        else:
            print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: invalid operation")
    except IndexError:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: no operation specified")
    except KeyboardInterrupt:
        print(f"{ANSI_CODES[0]}error{ANSI_CODES[4]}: user pressed CTRL+C so exiting")
        exit(1)

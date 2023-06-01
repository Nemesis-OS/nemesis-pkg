from sys import argv

mainpage = """
nemesis-pkg:
============
usage:- nemesis-pkg {operation} {args}
============
operations:-
i: installs a package.. nemesis-pkg i {pkg1} {pkg2}
r: removes a package... nemesis-pkg r {pkg1} {pkg2}
lsi: lists system installed packages.. nemesis-pkg lsi {pkg}
lri: lists packages in repository... nemesis-pkg lri {pkg}
ug: upgrade packages... nemesis-pkg ug
ud: update the package database... nemesis-pkg ud
h: shows info on operations and usage.. nemesis-pkg h
"""
operations = ["i" , "r" , "lsi" , "lri" , "ug" , "ud" , "h"]
path_pkglist = "/etc/nemesis-pkg/PKGLIST"
path_ipkglist = "/e"

if __name__ == "__main__":
    try:
        if argv[1] == "h":
            print(mainpage)
        else:
            print("error: invalid operation")
    except IndexError:
        print("error: no operation specified")

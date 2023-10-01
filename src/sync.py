from os.path import isfile
from subprocess import check_output, CalledProcessError

def get_raw_file(url: str):
    '''
    this function converts the URL into the file which it needs to be stored.. https://sample.com/test.PKGLIST to test.PKGLIST 
    '''
    return url.split("/")[len(url.split("/"))-1]
    
def sync(PKGLIST: str):
    '''
    sync(PKGLIST): here PKGLIST has to be entered and then it sync's it... 
    this function returns 0,1,2.. 0 = updated.. 1 = up-to-date, 2 = error
    '''
    if isfile(f"/etc/nemesis-pkg/{get_raw_file(PKGLIST)}") == True:
        try:
            contents = check_output(['curl', PKGLIST]).decode('utf-8')
        except CalledProcessError:
            return 2

        with open(f"/etc/nemesis-pkg/{get_raw_file(PKGLIST)}", 'r+') as repofile:
            dbc = repofile.read()
            if dbc == contents:
                repofile.close()
                return 1
            else:
                repofile.seek(0)
                repofile.write(contents)
                repofile.truncate()
                repofile.close()
                return 0
    else:
        try:
            contents = check_output(['curl', PKGLIST, '-o', f'/etc/nemesis-pkg/{get_raw_file(PKGLIST)}']).decode('utf-8')
        except CalledProcessError:
            return 2
        else:
            return 0

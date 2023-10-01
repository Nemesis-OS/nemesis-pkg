def vtoi(version: str):
    '''
    vtoi(version): here converts version to integer
    vtoi("22.10") -> 2210  
    '''
    ver = list(version)
    version = ""
    for i in ver:
        try:
            version = version+str(int(i))
        except ValueError:
            continue

    return int(version)

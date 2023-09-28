'''
printutils: a lib for npkg to show term output during errors/warning/sucess/note/input 

colors:
- error: red
- sucess: green
- note: blue
- warning: yellow
- input: magenta
'''

def puinput(text: str):
    '''
    puinput(text: str).. here input will be shown as INPUT: text
    '''
    return input(f"\x1b[95mINPUT\x1b[0m: {text} ")

def puerror(text: str):
    '''
    puerror(text).. here prints error as ERROR: text  
    '''
    print(f"\x1b[91mERROR\x1b[0m: {text}")

def puinfo(text: str):
    '''
    puinfo(text).. here prints info as INFO: text  
    '''
    print(f"\x1b[94mINFO\x1b[0m: {text}")

def puwarn(text: str):
    '''
    puwarn(text)... here prints warning as WARNING: text  
    '''
    print(f"\x1b[93mWARNING\x1b[0m: {text}")

def pupass(text: str):
    '''
    pupass(text).. here prints passed operation as PASS: text  
    '''
    print(f"\x1b[92mPASS\x1b[0m: {text}")

levels = {"CRITICAL":0, "ERROR":1, "WARNING":2,"INFO":3,"DEBUG":4,"TRACE":5}

loglevel = "DEBUG"

def log(levelstring, string, printlist=[]):
    if levels[levelstring] > levels[loglevel]:
        return
    
    print("[",levelstring,"]", string, end=' ')
    for e in printlist:
        print(e, end=' ')
    
    print("", end='\n')
    return

'''
NAME: Server Resource LOgger
VERSION: 0.1v
LAST UPDATED: January 25, 2020
CREATED BY: Matthew
'''
import psutil
import datetime
import threading, time

# CONFIGURATION VARIABLES
logPath = "usageLog.txt" # path to log file ; DEFAULT: usageLog.txt
checksBeforeLog = 10 # logging interval in seconds (s) ; DEFAULT: 20
checkInterval = 30 # checking interval in seconds (s) ; DEFAULT: 30

# GLOBAL VARIABLES
x = 0 # interval counter
cpuL = []
storageL = []
virtualL = []
swapL = []

def getCPU(): # CPU
    '''() -> [total usage, per core usage, core count, logical core count]'''
    return [psutil.cpu_percent(interval=1), psutil.cpu_percent(interval=1, percpu=True), psutil.cpu_count(), psutil.cpu_count(logical=False)]

def getVirtualMemory(): # virtual memory
    '''() -> [total memory in (GB), memory usage]'''
    VirtualMem = psutil.virtual_memory()
    return [VirtualMem.total / (1024.0 ** 3), VirtualMem.percent]

def getSwapMemory(): # swap memory
    '''() -> [total swap memory (GB), memory usage]'''
    SwapMem = psutil.swap_memory()
    return [SwapMem.total / (1024.0 ** 3), SwapMem.percent]

def getStorage(): # storage
    '''() -> [total storage (GB), percent used]'''
    diskUsage = psutil.disk_usage("/")
    return [diskUsage.total / (1024.0 ** 3), diskUsage.percent]

def logger(cpu, storage, swap, virtual): # logs data
    global logPath
    content = f"[[{round(min(cpu))},{round(max(cpu))},{round(sum(cpu)/len(cpu))}],[{round(min(virtual))},{round(max(virtual))},{round(sum(virtual)/len(virtual))}],[{round(min(swap))},{round(max(swap))},{round(sum(swap)/len(swap))}],[{round(sum(storage)/len(storage))}],[{datetime.datetime.now().strftime('%d.%m.%Y')},{datetime.datetime.now().strftime('%H:%M:%S')}]]\n"
    output = open(logPath,'a+')
    output.write(content)
    output.close()

def compileInfo(wipe=False): # compiles recent data
    global cpuL
    global storageL
    global virtualL
    global swapL
    if wipe == True:
        cpuL = []
        storageL = []
        virtualL = []
        swapL = []
    else:
        cpuL.append(getCPU()[0])
        storageL.append(getStorage()[1])
        virtualL.append(getVirtualMemory()[1])
        swapL.append(getSwapMemory()[1])

# cycles through compiling and logging data
def startThreads():
    checkEvent = threading.Event()
    while not checkEvent.wait(checkInterval):
        global x
        if x >= checksBeforeLog:
            logger(cpuL, storageL, swapL, virtualL)
            compileInfo(True)
            x = 0
        else:
            compileInfo()
            x += 1

startThreads() # starts the program
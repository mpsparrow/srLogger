'''
NAME: srLogger (Server Resource Logger)
VERSION: 0.2v
LAST UPDATED: January 30, 2020
CREATED BY: Matthew
'''
import psutil
import datetime
import threading, time

class Usage:
    def __init__(self, path, checks, intervals):
        self.path = path
        self.checks = checks
        self.intervals = intervals
        self.x = 0
        self.cpuL = []
        self.vmemoryL = []
        self.smemoryL = []
        self.storageL = []

    def getCoreCount(self):
        return psutil.cpu_count()

    def getCoreCountLogical(self):
        return psutil.cpu_count(logical=False)

    def getCPUpercentCore(self):
        return psutil.cpu_percent(interval=1, percpu=True)

    def getCPUpercent(self):
        return psutil.cpu_percent(interval=1)

    def getCPUpercentAvg(self):
        return round(sum(self.cpuL)/len(self.cpuL), 1)

    def getVMemoryAmount(self):
        return VirtualMem.total / (1024.0 ** 3)

    def getVMemoryPercent(self):
        return VirtualMem.percent

    def getVMemoryPercentAvg(self):
        return round(sum(self.vmemoryL)/len(self.vmemoryL), 1)

    def getSMemoryAmount(self):
        return SwapMem.total / (1024.0 ** 3)

    def getSMemoryPercent(self):
        return SwapMem.percent

    def getSMemoryPercentAvg(self):
        return round(sum(self.smemoryL)/len(self.smemoryL), 1)

    def getStorageAmount(self):
        return diskUsage.total / (1024.0 ** 3)

    def getStoragePercent(self):
        return diskUsage.percent

    def getStoragePercentAvg(self):
        return round(sum(self.storageL)/len(self.storageL), 1)

    def getDate(self):
        return datetime.datetime.now().strftime('%d.%m.%Y')
    
    def getTime(self):
        return datetime.datetime.now().strftime('%H:%M:%S')

    def compileInfo(self, wipe=False):
        if wipe == True:
            self.cpuL = []
            self.vmemoryL = []
            self.smemoryL = []
            self.storageL = []
        else:
            self.cpuL.append(self.getCPUpercent())
            self.vmemoryL.append(self.getVMemoryPercent)
            self.smemoryL.append(self.getSMemoryPercent)
            self.storageL.append(self.getStoragePercent)

    def logger(self):
        content = f"[[{self.getCPUpercentAvg()}],[{self.getSMemoryPercentAvg()}],[{self.getDate()},{self.getTime()}]]\n"
        output = open(self.path,'a+')
        output.write(content)
        output.close()

    def thread(self):
        checkEvent = threading.Event()
        while not checkEvent.wait(self.intervals):
            if self.x >= self.checks:
                self.logger()
                self.compileInfo(True)
                self.x = 0  
            else:
                self.compileInfo()
                self.x += 1

task1 = Usage("usageLog.txt", 10, 30)
task1.thread()
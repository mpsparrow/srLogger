'''
NAME: srLogger (Server Resource Logger)
VERSION: 0.2v
LAST UPDATED: January 30, 2020
CREATED BY: Matthew
'''
import psutil
import datetime
import threading, time
import mysql.connector as mysql
from mysql.connector import errorcode

def SQLconnect(values):
    try:
        cnx = mysql.connect(user='', password='', host='localhost', database='')
    except mysql.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cursor = cnx.cursor()
        try:
            cursor.execute("CREATE TABLE `usage` (`date` DATE, `time` TIME, `cpu_core_count` INT(255), `cpu_core_count_logical` INT(255), `cpu_percent` DOUBLE(3, 1), `cpu_percent_avg` DOUBLE(3, 1))")
        except:
            pass
        query = "INSERT INTO `usage` (date, time, cpu_core_count, cpu_core_count_logical, cpu_percent, cpu_percent_avg) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, values)
        cnx.commit()
        cnx.close()

class Usage:
    def __init__(self, checks, intervals):
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
        return psutil.virtual_memory().total / (1024.0 ** 3)

    def getVMemoryPercent(self):
        return psutil.virtual_memory().percent

    def getVMemoryPercentAvg(self):
        return round(sum(self.vmemoryL)/len(self.vmemoryL), 1)

    def getSMemoryAmount(self):
        return psutil.swap_memory().total / (1024.0 ** 3)

    def getSMemoryPercent(self):
        return psutil.swap_memory().percent

    def getSMemoryPercentAvg(self):
        return round(sum(self.smemoryL)/len(self.smemoryL), 1)

    def getStorageAmount(self):
        return psutil.disk_usage("/").total / (1024.0 ** 3)

    def getStoragePercent(self):
        return psutil.disk_usage("/").percent

    def getStoragePercentAvg(self):
        return round(sum(self.storageL)/len(self.storageL), 1)

    def getDate(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')
    
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
        value = (self.getDate(), self.getTime(),self.getCoreCount(), self.getCoreCountLogical(), self.getCPUpercent(), self.getCPUpercentAvg())
        SQLconnect(value)

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

task1 = Usage(2, 2)
task1.thread()
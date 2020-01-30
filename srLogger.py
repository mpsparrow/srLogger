'''
NAME: srLogger (Server Resource Logger)
VERSION: 0.3v
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
            cursor.execute("""CREATE TABLE `usage` (
                `date` DATE, `time` TIME,
                `cpu_percent_avg` DOUBLE(3, 1), `cpu_min` DOUBLE(3, 1), `cpu_max` DOUBLE(3, 1),
                `vmemory_percent_avg` DOUBLE(3, 1), `vmemory_min` DOUBLE(3, 1), `vmemory_max` DOUBLE(3, 1),
                `smemory_percent_avg` DOUBLE(3, 1), `smemory_min` DOUBLE(3, 1), `smemory_max` DOUBLE(3, 1),
                `storage_percent` DOUBLE(3, 1), `storage_gb_usage` DOUBLE(10, 1)
                )""")
        except:
            pass
        query = """INSERT INTO `usage` (
            date, time, 
            cpu_percent_avg, cpu_min, cpu_max,
            vmemory_percent_avg, vmemory_min, vmemory_max,
            smemory_percent_avg, smemory_min, smemory_max,
            storage_percent, storage_gb_usage
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
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

    def getCPUmin(self):
        return min(self.cpuL)

    def getCPUmax(self):
        return max(self.cpuL)

    def getVMemoryAmount(self):
        return round(psutil.virtual_memory().total / (1024.0 ** 3), 1)

    def getVMemoryPercent(self):
        return psutil.virtual_memory().percent

    def getVMemoryPercentAvg(self):
        return round(sum(self.vmemoryL)/len(self.vmemoryL), 1)

    def getVMemoryMin(self):
        return min(self.vmemoryL)

    def getVMemoryMax(self):
        return max(self.vmemoryL)

    def getSMemoryAmount(self):
        return psutil.swap_memory().total / (1024.0 ** 3)

    def getSMemoryPercent(self):
        return psutil.swap_memory().percent

    def getSMemoryPercentAvg(self):
        return round(sum(self.smemoryL)/len(self.smemoryL), 1)

    def getSMemoryMin(self):
        return min(self.smemoryL)

    def getSMemoryMax(self):
        return max(self.smemoryL)

    def getStorageAmount(self):
        return psutil.disk_usage("/").used / (1024.0 ** 3)

    def getStoragePercent(self):
        return psutil.disk_usage("/").percent

    def getDate(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')
    
    def getTime(self):
        return datetime.datetime.now().strftime('%H:%M:%S')

    def compileInfo(self, wipe=False):
        if wipe == True:
            self.cpuL = []
            self.vmemoryL = []
            self.smemoryL = []
        else:
            self.cpuL.append(self.getCPUpercent())
            self.vmemoryL.append(self.getVMemoryPercent())
            self.smemoryL.append(self.getSMemoryPercent())

    def logger(self):
        value = (self.getDate(), self.getTime())
        value += (self.getCPUpercentAvg(), self.getCPUmin(), self.getCPUmin())
        value += (self.getVMemoryPercentAvg(), self.getVMemoryMin(), self.getVMemoryMax())
        value += (self.getSMemoryPercentAvg(), self.getSMemoryMin(), self.getSMemoryMax())
        value += (self.getStoragePercent(), self.getStorageAmount())
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

task1 = Usage(10, 30)
task1.thread()
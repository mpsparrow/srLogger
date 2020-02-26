import psutil
import datetime
import threading, time
import mysql.connector as mysql
from mysql.connector import errorcode

class srLogger:
    def __init__(self):
        # threads
        self.checks = None
        self.intervals = None
        self.threadRun = False
        self.x = 0
        # logging
        self.cpuL = []
        self.cpuAvg = []
        self.vmemoryL = []
        self.vmemoryAvg = []
        self.smemoryL = []
        self.smemoryAvg = []
        # database
        self.user = None
        self.password = None
        self.host = None
        self.database = None
        self.table = None

    def getCoreCount(self):
        return psutil.cpu_count()

    def getCoreCountLogical(self):
        return psutil.cpu_count(logical=False)

    def getCPUpercentCore(self):
        return psutil.cpu_percent(interval=1, percpu=True)

    def getCPUpercent(self):
        return psutil.cpu_percent(interval=1)

    def getCPUpercentAvg(self):
        if len(self.cpuAvg) >= 5:
            self.cpuAvg.pop()
        self.cpuAvg.append(round(sum(self.cpuL)/len(self.cpuL), 1))
        return round(sum(self.cpuAvg)/len(self.cpuAvg), 1)

    def getCPUmin(self):
        return min(self.cpuL)

    def getCPUmax(self):
        return max(self.cpuL)

    def getVMemoryAmount(self):
        return round(psutil.virtual_memory().total / (1024.0 ** 3), 1)

    def getVMemoryPercent(self):
        return psutil.virtual_memory().percent

    def getVMemoryPercentAvg(self):
        if len(self.vmemoryAvg) >= 5:
            self.vmemoryAvg.pop()
        self.vmemoryAvg.append(round(sum(self.vmemoryL)/len(self.vmemoryL), 1))
        return round(sum(self.vmemoryAvg)/len(self.vmemoryAvg), 1)

    def getVMemoryMin(self):
        return min(self.vmemoryL)

    def getVMemoryMax(self):
        return max(self.vmemoryL)

    def getSMemoryAmount(self):
        return psutil.swap_memory().total / (1024.0 ** 3)

    def getSMemoryPercent(self):
        return psutil.swap_memory().percent

    def getSMemoryPercentAvg(self):
        if len(self.smemoryAvg) >= 5:
            self.smemoryAvg.pop()
        self.smemoryAvg.append(round(sum(self.smemoryL)/len(self.smemoryL), 1))
        return round(sum(self.smemoryAvg)/len(self.smemoryAvg), 1)

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

    def setDB(self, user, password, host, database, table):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.table = table

    def connectDB(self, values):
        try:
            cnx = mysql.connect(user=self.user, password=self.password, host=self.host, database=self.database)
        except mysql.Error as err:
            print(err)
        else:
            cursor = cnx.cursor()
            try:
                cursor.execute(f"""CREATE TABLE `{self.table}` (
                    `date` DATE, `time` TIME,
                    `cpu_percent_avg` DOUBLE(3, 1), `cpu_min` DOUBLE(3, 1), `cpu_max` DOUBLE(3, 1),
                    `vmemory_percent_avg` DOUBLE(3, 1), `vmemory_min` DOUBLE(3, 1), `vmemory_max` DOUBLE(3, 1),
                    `smemory_percent_avg` DOUBLE(3, 1), `smemory_min` DOUBLE(3, 1), `smemory_max` DOUBLE(3, 1),
                    `storage_percent` DOUBLE(3, 1), `storage_gb_usage` DOUBLE(10, 1)
                    )""")
            except:
                pass
            query = f"""INSERT INTO `{self.table}` (
                date, time, 
                cpu_percent_avg, cpu_min, cpu_max,
                vmemory_percent_avg, vmemory_min, vmemory_max,
                smemory_percent_avg, smemory_min, smemory_max,
                storage_percent, storage_gb_usage
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, values)
            cnx.commit()
            cnx.close()

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
        values = (self.getDate(), self.getTime())
        values += (self.getCPUpercentAvg(), self.getCPUmin(), self.getCPUmax())
        values += (self.getVMemoryPercentAvg(), self.getVMemoryMin(), self.getVMemoryMax())
        values += (self.getSMemoryPercentAvg(), self.getSMemoryMin(), self.getSMemoryMax())
        values += (self.getStoragePercent(), self.getStorageAmount())
        self.connectDB(values)

    def setThread(self, intervals, checks):
        self.checks = checks
        self.intervals = intervals

    def thread(self):
        checkEvent = threading.Event()
        self.threadRun = True
        while not checkEvent.wait(self.intervals) and self.threadRun:
            if self.x >= self.checks:
                self.logger()
                self.compileInfo(True)
                self.x = 0  
            else:
                self.compileInfo()
                self.x += 1
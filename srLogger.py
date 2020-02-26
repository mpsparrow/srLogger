'''
NAME: Server Resource Logger (srLogger)
VERSION: 0.4v
LAST UPDATED: February 26, 2020
CREATED BY: Matthew
'''
import function as sr

# sample config
task1 = sr.srLogger()
task1.setDB(user, password, host, database, table)
task1.setThread(5, 5)
task1.thread()
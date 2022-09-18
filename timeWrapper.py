from sqlite3 import Time
import time
import numpy as np

class TimeWrapper:
    global_time = 0
    epoch = 0

    #Gets current time in seconds from 1970 and uses it as a point of reference for time calculatiobs
    def __init__(self):
        self.startTime()


    def startTime(self):
        self.epoch = time.time()
        self.updateCurrentTime()

    #Gets current time
    
    def updateCurrentTime(self):
        
        self.global_time = time.time() - self.epoch
        

    #Returns a 2 by 1 matrix containing the time displacement
    def getDt(self):
        t_0 = self.global_time
        self.updateCurrentTime()
        dt_matrix = [self.global_time-t_0,1]
        
        return dt_matrix

from unicodedata import name
import pandas as pd
import os.path

class ReadWriteCSV:
    def __init__(self, name_of_file = 'data.csv', operation = 'read'):
        self.mode = 'w'
        self.path = name_of_file
        self.df = pd.DataFrame()
  
        
        if operation == 'write':
            self.df.to_csv(name_of_file, sep = '|', index= False, header=False)
            self.mode = 'a'
        
        else:
            self.mode = 'r'



    def writeCSV(self,data):
        self.df = pd.DataFrame(data=data)
        self.df.to_csv(self.path, sep = '|', mode='a', index= False,header=False)


    def readCSV(self):
        if(self.mode=='r'):
            df = pd.read_csv(self.path, index_col=0)
            return df
        else:
            print("Object of class \"ReadWriteCSV\" is set on write")


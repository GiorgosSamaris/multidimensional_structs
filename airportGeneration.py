
import math as mth

class AirportGeneration:
    #constant
    global pi
    pi = 3.1416

    #constructor
    def __init__(self,mpWidth,mpHeight):
        self.mapWidth = mpWidth
        self.mapHeight = mpHeight
        


    # idBasedSearch is used for searching the lists containing the openFlight datasets. 
    # Ids are tokens created by openFlights and are used to identify an entry. 
    # They are asigned in an incremental order but are not incremented unary.
    def idBasedSearch(self,id, list):  
    
        entry = int(), int(),int()
        #check if the openFlights id-1 matches the list index
        if (id - 1)<len(list):                          
            entry = list[id-1]
            if id == entry[0]:     
                return entry [1], entry[2]

        #if not, search the list for the id
        for entry in list:                              
            if id == entry[0]:
                break
        return entry [1], entry[2]



    def mercatorTransform(self,lat, long):
        
        m_x = (long + 180)*(self.mapWidth/360) 

        #converting latitude from degrees to radiants
        latRad = lat*pi/180

        
        mercN = mth.log(mth.tan((pi/4)+(latRad/2)))
        m_y = (self.mapHeight/2) - (self.mapWidth*mercN/(2*pi))
        return int(m_x), int(m_y)
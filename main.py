from ast import Eq
from ctypes import sizeof
import math as mth
from tkinter import ANCHOR
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import re
import random as rand
from numpy import dsplit
import time 
import numpy as np

#definitions
mapWidth = 2058
mapHeight = 2058
pi = 3.1416
epoch = 0.000
time_global = 0.000
dx_matrix = np.array(1)
line_matrix = np.array(1)
result_x = np.array()
result_y = np.array()


#//////////////////////////////////////////////MISC.////////////////////////////////////////////////////
def listToArray(primary_list):
    np_arr_x = np.array(len(primary_list))
    np_arr_y = np.array(len(primary_list))
    for i in primary_list:                  #i[0]:airport id, i[1]:x_coord, i[2]:y_coord
        np_arr_x = np.append(np_arr_x,i[1])
        np_arr_y = np.append(np_arr_y,i[2])
    return np_arr_x,np_arr_y



def readGisData(file_path):
    m_list = []

    m_file =  open(file_path)
    num_lines_read = 0

    while True:
        curr_line = m_file.readline()
        if not curr_line:
            break
        m_tuple = re.split(r',(?!\s)',curr_line)                #regex to avoid commas inside quotations 
        #print(m_tuple)
        m_list.append(m_tuple)
        num_lines_read += 1

    

    m_file.close()
    print('In file: '+str(file_path)+', '+str(num_lines_read)+' lines were read.')
    return m_list



# idBasedSearch is used for searching the lists containing the openFlight datasets. 
# Ids are tokens created by openFlights and are used to identify an entry. 
# They are asigned in an incremental order but are not incremented unary.
def idBasedSearch(id, list):  
    
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



def mercatorTransform(long, lat):

    m_x = (long + 180)*(mapWidth/360) 

    #converting latitude from degrees to radiants
    latRad = lat*pi/180
    
    
    mercN = mth.log(mth.tan((pi/4)+(latRad/2)))
    m_y = (mapHeight/2) - (mapWidth*mercN/(2*pi))
    return int(m_x), int(m_y)



#/////////////////////////////////////////////ROUTE-LINES///////////////////////////////////////////////

#Given the source and destination of the aircraft getDomain returns the x and y domain of the 
#line equation
def getDomain(a_coords,b_coords):
    
    tmp = int()
    x_min,x_max = a_coords[0],b_coords[0]
    y_min,y_max = a_coords[1],b_coords[1]   
    if x_max<x_min:
        tmp = x_max
        x_max = x_min
        x_min = tmp

    if  y_max<y_min:
        tmp = y_max
        y_max = y_min
        y_min = tmp
    
    x_domain = x_min,x_max
    y_domain = y_min,y_max
    return x_domain, y_domain


def routeToEquation(start,end):
    try:
        #find slope of line eq
        slope = float((end[1] - start[1])/(end[0]-start[0]))#1 is for y and 0 is for x
     
        #find constant c of line eq
        c = float(end[1] - slope*end[0])
        return slope, c 
    except ZeroDivisionError:
        return None,None



#///////////////////////////////////////////////PLANES/////////////////////////////////////////////////////
def generatePlane(plane_list, route_id):
    #icao,route_id,vel,x,y,t
    plane = str(),int(),int(),int(),int,float()           
    
    #choose a random plane from the list
    index = rand.randint(0,len(plane_list)-1)
    choice = plane_list[index]

    #get the icao number from openFlights
    icao = str(choice[2])             

    #give a random velocity value to the generated plane                          
    velocity = rand.randint(600,900)
    
    t_0 = time_global

    x_0 = None
    y_0 = None

    plane = icao, route_id, velocity, x_0, y_0, t_0 
    return plane


def getVelocityX(velocity,slope):
    #REMEMBER TO CHECK FOR SLOPE NONE 
    try:
        #calculate the vertex x of velocity
        velocity_x = velocity/((1-slope)*(1+slope))
    except ZeroDivisionError:
        velocity_x = mth.sin(45)*velocity
    return velocity_x






#////////////////////////////////////////////TIME_FUNCTIONS////////////////////////////////////////////

#Gets current time in seconds from 1970 and uses it as a point of reference for time calculatiobs
def timeInit():
    epoch = time.time()

#Gets current time
def updateCurrentTime():
    time_global = time.time() - epoch
    
#Returns a 2 by 1 matrix containing the time displacement
def getDt():
    t_0 = time_global
    updateCurrentTime()
    dt_matrix = np.array([time_global-t_0,1])
    return dt_matrix


#/////////////////////////////////////TRANSFORM MATRICES//////////////////////////////////////////////

def appendDxMatrix(velocity,slope,x_0):
    global dx_matrix
    velocity_x = getVelocityX(velocity,slope)
    temp_array = np.array([velocity_x,x_0])
    dx_matrix = np.append(dx_matrix,temp_array)

def appendLineMatrix(slope,c):
    global line_matrix
    temp_array = np.array([slope,c])
    line_matrix = np.append(line_matrix,temp_array)


def generateTransformMatrices(plane_list,line_list):
    for plane in plane_list:
        route_id = plane[1]
        line_eq = line_list[route_id]
        slope = line_eq[0]
        c = line_eq[1]
        velocity = plane[2]
        x_0 = plane[3]
        appendDxMatrix(velocity,slope,x_0)
        appendLineMatrix(slope,c)
    
#implimentation of planePos but with matrix multiplication
def updateAllPlanePos():
    global result_y
    global result_x
    #get time displacement matrix
    dt = getDt()
    result_x = np.matmul(dx_matrix,dt)
    result_y = np.matmul(result_x,line_matrix)



def planePos(plane,line_equations):
    #get the route_id and retrieve the line equation from the list 
    route_id = plane[1]
    line_eq = line_equations[route_id]

    #get data from the lists
    slope = line_eq[0]
    c = line_eq[1]
    velocity = plane[2]
    x_0 = plane[3]
    y_0 = plane[4]
    t_0 = plane[5]
    src_coords = line_eq[4]
    
    #find the sign (direction) of velocity
    sign = velocity/abs(velocity)  

    
    
    try:
        #calculate the vertex x of velocity
        velocity_x = velocity/((1-slope)*(1+slope))
        #find the displacement of x 
        x = velocity_x*(time_global - t_0)+ x_0
        #calculate y
        y = slope*x + c
        return x,y
    except ZeroDivisionError:
        return x_0,y_0




        




def main():
    airport_list = readGisData("airports.dat.txt")
    plane_list = readGisData("planes.dat.txt")
    route_list = readGisData("routes.dat.txt")
    rand.seed(10)

   
    #////////////////////////////////////////////////////////////////////////////////////////////
    port_loc = []
    
    for data in airport_list:

        lat = float(data[6])
        long = float(data [7])
        id = int(data[0])

        x, y = mercatorTransform(long,lat)
        tmp_tuple = id, x, y
    
        port_loc.append(tmp_tuple)
        
        

    #/////////////////////////////////////////////////////////////////////////////////////////////
    line_eqs = []

    for data in route_list:
        if "\\N" != data[5] and "\\N" != data[3]:                #Some entries have a null identifier 
                                                                 #so we reject them entirely   
            src_airport = int(data[3])                           #Get the id of the source and destination airports
            dst_airport = int(data[5])   
            
            src_coords = idBasedSearch(src_airport,port_loc)     #search for the source airport and get its coords
            dst_coords = idBasedSearch(dst_airport,port_loc)


            slope, c =routeToEquation(src_coords,dst_coords)     #find the line equation for the specified route

            x_domain,y_domain = getDomain(src_coords,dst_coords)    #get the domain for the specified route


            tmp_tuple = slope,c,x_domain,y_domain , src_coords, dst_coords   #insert data to a tuple and append it                                      
            line_eqs.append(tmp_tuple)
    
    print("route creation completed!")
    print(str(len(line_eqs))+" lines generated")

    #///////////////////////////////////////////////////////////////////////////////////////////////////
    #generate planes and assign them to a route
    route_id = 0
    active_planes = []
    for data in line_eqs:
        plane = generatePlane(plane_list,route_id)
        active_planes.append(plane)
        route_id +=1
    print(str(len(active_planes))+" planes generated and assigned to a route successfuly!")
    print("beginning simulation...")
    
    
    
    



    #///////////////////////////////////////////////////////////////////////////////////////////
    x_coords,y_coords = listToArray(port_loc)
    img = mpimg.imread('map.jpeg')
    imgplot = plt.imshow(img)
    plt.xlim(0, mapWidth)
    plt.ylim(mapHeight,0)
    plt.scatter(x_coords,y_coords,color='red',s=1.5)
    plt.show(imgplot)

if __name__ == "__main__":
    main() 
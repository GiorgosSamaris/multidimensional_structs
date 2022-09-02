from ast import Eq
from ctypes import sizeof
import math as mth
import timeWrapper as tw
import planeGeneration as plane
import routeGeneration as route
import airportGeneration as port
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

dx_matrix = np.array(1)
line_matrix = np.array(1)
result_x = np.array(1)
result_y = np.array(1)


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

    m_file =  open(file_path,encoding="utf8")
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




def main():
    airport_list = readGisData("airports.dat.txt")
    plane_list = readGisData("planes.dat.txt")
    route_list = readGisData("routes.dat.txt")
    rand.seed(10)
    tm = tw.TimeWrapper()
    pln = plane.PlaneGeneration()
    prt = port.AirportGeneration(mapWidth,mapHeight)
    rt = route.RouteGeneration()


    #////////////////////////////////////////////////////////////////////////////////////////////
    port_loc = []
    
    for data in airport_list:

        lat = float(data[6])
        long = float(data [7])
        id = int(data[0])
        
        x, y = prt.mercatorTransform(lat,long)
        tmp_tuple = id, x, y
    
        port_loc.append(tmp_tuple)
        
        

    #/////////////////////////////////////////////////////////////////////////////////////////////
    line_eqs = []

    for data in route_list:
        if "\\N" != data[5] and "\\N" != data[3]:                #Some entries have a null identifier 
                                                                 #so we reject them entirely   
            src_airport = int(data[3])                           #Get the id of the source and destination airports
            dst_airport = int(data[5])   
            
            src_coords = prt.idBasedSearch(src_airport,port_loc)     #search for the source airport and get its coords
            dst_coords = prt.idBasedSearch(dst_airport,port_loc)


            slope, c = rt.routeToEquation(src_coords,dst_coords)     #find the line equation for the specified route

            x_domain,y_domain = rt.getDomain(src_coords,dst_coords)    #get the domain for the specified route


            tmp_tuple = slope,c,x_domain,y_domain , src_coords, dst_coords   #insert data to a tuple and append it                                      
            line_eqs.append(tmp_tuple)
    
    print("route creation completed!")
    print(str(len(line_eqs))+" lines generated")

    #///////////////////////////////////////////////////////////////////////////////////////////////////
    #generate planes and assign them to a route
    route_id = 0
    active_planes = []
    for data in line_eqs:
        p = pln.generatePlane(plane_list,route_id)
        active_planes.append(p)
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
    plt.show()

if __name__ == "__main__":
    main() 
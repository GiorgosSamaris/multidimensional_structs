import timeWrapper as tw
import planeGeneration as plane
import routeGeneration as route
import airportGeneration as port
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import re
import random as rand
from PIL import Image
import numpy as np
from matplotlib.animation import FuncAnimation 
import read_write_csv as csvW
import rTree as rtr


#definitions
mapWidth = 2058
mapHeight = 2058
tm = tw.TimeWrapper()
pln = plane.PlaneGeneration(tm)
prt = port.AirportGeneration(mapWidth,mapHeight)
rt = route.RouteGeneration()
wrt = csvW.ReadWriteCSV(operation='write')

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


def initRTree(t_1,t_2,active_planes,b=10):
    r = rtr.RTree(b)
    x_1,y_1 = pln.calcDisplacement(0,t_1)
    x_2,y_2 = pln.calcDisplacement(t_1,t_2,x_1)
    
    plt.plot([x_1,x_2],[y_1,y_2],color='black')

    for i, plane in enumerate(active_planes):
        mbr = rtr.MinBoundingRectangle([x_1[i],x_2[i]], [y_1[i],y_2[i]],
        [t_1,t_2])
        print(i)
        obj = rtr.Object(plane,mbr)
        
        r.insert(obj)
    return r

def query(mbr,active_planes,b_factor = 10):
    print("creating tree...")
    r = initRTree(mbr.t[0],mbr.t[1],active_planes,b_factor)
    query_response = r.search(r.root,mbr)
    print("tree creation completed successfuly")
    return query_response



def animate(i):
    result_x,result_y = pln.updateAllPlanePos()
    time_stamp=tm.global_time
    time = np.full(len(result_x), time_stamp)
    stacked = np.vstack([result_x,result_y,time])
    wrt.writeCSV(stacked.T)
    
    plt.scatter(result_x,result_y,color='black',s=0.05)

def main():
    plt.figure()  
    img = mpimg.imread('map.jpeg')
    plt.xlim(0,mapWidth)
    plt.ylim(mapHeight,0)
    imgplot = plt.imshow(img)


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


            tmp_tuple = slope, c, x_domain, y_domain, src_coords, dst_coords   #insert data to a tuple and append it                                      
            line_eqs.append(tmp_tuple)
    
    print("route creation completed!")
    print(str(len(line_eqs))+" lines generated")

    #///////////////////////////////////////////////////////////////////////////////////////////////////
    #generate planes and assign them to a route
    route_id = 0
    active_planes = []
    for data in line_eqs:
        p = pln.generatePlane(plane_list,route_id,data)
        active_planes.append(p)
        route_id +=1
    print(str(len(active_planes))+" planes generated and assigned to a route successfuly!")
    
    
    x_coords,y_coords = listToArray(port_loc)
    plt.scatter(x_coords,y_coords,color='red',s=0.1)
   
    
    pln.generateTransformMatrices(active_planes[:1000],line_eqs[:1000])
    
    
    

    mbr_q = rtr.MinBoundingRectangle([1000,1230],[600,814],[0,1])

    query_response = query(mbr_q,active_planes[:1000],75)

    print("items found inside: " + str(len(query_response)))

    
    
    plt.figure()
    plt.imshow(img)
    plt.title("items found inside: " + str(len(query_response)))
    plt.xlim(mbr_q.x)
    plt.ylim(mbr_q.y[1],mbr_q.y[0])
    for obj in query_response:
        mbr = obj.mbr
        
        plt.plot([mbr.x[0],mbr.x[1]],[mbr.y[0],mbr.y[1]])

    
    plt.show()

if __name__ == "__main__":
    main() 
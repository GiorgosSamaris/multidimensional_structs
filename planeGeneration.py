from ctypes import sizeof
import random as rand
import math as mth
import timeWrapper as tw
import numpy as np

class PlaneGeneration:
    


    def __init__(self,time_obj) :
        self.dx_matrix = np.empty((0,2))
        self.line_matrix = np.empty((0,2))
        self.tm = time_obj
        
    def generatePlane(self,plane_list, route_id,route):
    #icao,route_id,vel,x,y,t
        #print("Route is: "+str(route))
        plane = str(),int(),int(),int(),int,float()           

        #choose a random plane from the list
        index = rand.randint(0,len(plane_list)-1)
        choice = plane_list[index]

        #get the icao number from openFlights
        icao = str(choice[2])             
        velocity = rand.randint(10,30)

        #give a random velocity value to the generated plane                          
       
        t_0 = self.tm.global_time

        start_point = route[4]
        
        x_0 = start_point[0]
        y_0 = start_point[1]
        

        plane = icao, route_id, velocity, x_0, y_0, t_0 
        return plane




    def getVelocityX(self,velocity,slope,src,dst):
        sign = 1
        
        #REMEMBER TO CHECK FOR SLOPE NONE 
        if dst[0] - src[0] > 0:
           sign = 1
        else: sign = -1
        try:
            #calculate the vertex x of velocity
            velocity_x = velocity/mth.sqrt(1+slope**2)
        except ZeroDivisionError:
            velocity_x = mth.sin(45)*velocity
        return velocity_x*sign

    #/////////////////////////////////////TRANSFORM MATRICES//////////////////////////////////////////////

    def updateDxMatrix(self):
        self.dx_matrix = np.delete(self.dx_matrix,1,axis=1)
        self.dx_matrix = np.column_stack((self.dx_matrix,result_x.T))
        #print(self.dx_matrix)



    def appendDxMatrix(self,velocity,slope,src,dst):
        #global dx_matrix
        velocity_x = self.getVelocityX(velocity,slope,src,dst)
        #print("velocity x: "+str(velocity_x))
        self.dx_matrix = np.vstack((self.dx_matrix,[velocity_x,src[0]]))
        #print("dx matrix: "+ str(self.dx_matrix))

    def appendLineMatrix(self,slope,c):
        #global line_matrix
        
        self.line_matrix = np.vstack((self.line_matrix,[slope,c]))
        #print("Line matrix: "+ str(self.line_matrix))


    def generateTransformMatrices(self,plane_list,line_list):
        for plane in plane_list:
            route_id = plane[1]
            line_eq = line_list[route_id]
            slope = line_eq[0]
            c = line_eq[1]
            velocity = plane[2]
            #x_0 = plane[3]
           
            #print("velocity x: "+ str(v_x))
            self.appendDxMatrix(velocity,slope,line_eq[4],line_eq[5])
            self.appendLineMatrix(slope,c)

    #implimentation of planePos but with matrix multiplication
    def updateAllPlanePos(self):
        global result_y
        global result_x
        #get time displacement matrix
        dt = self.tm.getDt()
        
        result_x = np.matmul(self.dx_matrix,dt)
        
        
        [a,b] = np.hsplit(self.line_matrix,2)
        
        a = a.flatten()
        
       
        temp_y = result_x*a
        temp_y = temp_y.flatten()
        
        b = b.flatten()
        
        
       
        result_y = np.add(temp_y,b)
        
        result_y = result_y.flatten()
       
        
        self.updateDxMatrix()
        return result_x,result_y
       


 
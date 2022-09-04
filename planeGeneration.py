import random as rand
import math as mth
import timeWrapper as tw
import numpy as np

class PlaneGeneration:
    


    def __init__(self,time_obj) :
        self.dx_matrix = np.empty((0,2))
        self.line_matrix = np.empty((2,0))
        self.tm = time_obj
        
    def generatePlane(self,plane_list, route_id,route):
    #icao,route_id,vel,x,y,t
        plane = str(),int(),int(),int(),int,float()           

        #choose a random plane from the list
        index = rand.randint(0,len(plane_list)-1)
        choice = plane_list[index]

        #get the icao number from openFlights
        icao = str(choice[2])             
        velocity = rand.randint(10,30)

        #give a random velocity value to the generated plane                          
       
        t_0 = self.tm.global_time

        start_point = route[5]
        x_0 = start_point[0]
        y_0 = start_point[1]
        

        plane = icao, route_id, velocity, x_0, y_0, t_0 
        return plane




    def getVelocityX(self,velocity,slope,src,dst):
        sign = 1
        slope = 0
        #REMEMBER TO CHECK FOR SLOPE NONE 
        if dst[0] - src[0] > 0:
           sign = 1
        else: sign = -1
        try:
            #calculate the vertex x of velocity
            velocity_x = velocity/((1-slope)*(1+slope))
        except ZeroDivisionError:
            velocity_x = mth.sin(45)*velocity
        return velocity_x*sign

    #/////////////////////////////////////TRANSFORM MATRICES//////////////////////////////////////////////

    def updateDxMatrix(self):
        self.dx_matrix = np.delete(self.dx_matrix,1,axis=0)
        #print(self.dx_matrix)
        self.dx_matrix = np.hstack([self.dx_matrix,result_x])


    def appendDxMatrix(self,velocity,slope,src,dst):
        #global dx_matrix
        velocity_x = self.getVelocityX(velocity,slope,src,dst)
        #print("velocity x: "+str(velocity_x))
        self.dx_matrix = np.append(self.dx_matrix,[velocity_x,src[0]])
        #print("dx matrix: "+ str(self.dx_matrix))

    def appendLineMatrix(self,slope,c):
        #global line_matrix
        
        self.line_matrix = np.append(self.line_matrix,[slope,c])
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
        one_matrix = np.ones(result_x.size)
        new_result_x = np.append(result_x,one_matrix)
       
        result_y = np.matmul(new_result_x,self.line_matrix)
        
        self.updateDxMatrix()
        return result_x,result_y
       


    #old function
    def planePos(self,plane,line_equations):
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
            x = velocity_x*(self.tm.global_time - t_0)+ x_0
            #calculate y
            y = slope*x + c
            return x,y
        except ZeroDivisionError:
            return x_0,y_0

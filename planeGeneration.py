import random as rand
import math as mth
import timeWrapper as tm
import numpy as np

class PlaneGeneration:
    def generatePlane(self,plane_list, route_id):
    #icao,route_id,vel,x,y,t
        plane = str(),int(),int(),int(),int,float()           

        #choose a random plane from the list
        index = rand.randint(0,len(plane_list)-1)
        choice = plane_list[index]

        #get the icao number from openFlights
        icao = str(choice[2])             

        #give a random velocity value to the generated plane                          
        velocity = rand.randint(600,900)

        t_0 = tm.global_time

        x_0 = None
        y_0 = None

        plane = icao, route_id, velocity, x_0, y_0, t_0 
        return plane


    def getVelocityX(self,velocity,slope):
        #REMEMBER TO CHECK FOR SLOPE NONE 
        try:
            #calculate the vertex x of velocity
            velocity_x = velocity/((1-slope)*(1+slope))
        except ZeroDivisionError:
            velocity_x = mth.sin(45)*velocity
        return velocity_x

    #/////////////////////////////////////TRANSFORM MATRICES//////////////////////////////////////////////

    def appendDxMatrix(self,velocity,slope,x_0):
        global dx_matrix
        velocity_x = self.getVelocityX(velocity,slope)
        temp_array = np.array([velocity_x,x_0])
        dx_matrix = np.append(dx_matrix,temp_array)

    def appendLineMatrix(self,slope,c):
        global line_matrix
        temp_array = np.array([slope,c])
        line_matrix = np.append(line_matrix,temp_array)


    def generateTransformMatrices(self,plane_list,line_list):
        for plane in plane_list:
            route_id = plane[1]
            line_eq = line_list[route_id]
            slope = line_eq[0]
            c = line_eq[1]
            velocity = plane[2]
            x_0 = plane[3]
            self.appendDxMatrix(velocity,slope,x_0)
            self.appendLineMatrix(slope,c)

    #implimentation of planePos but with matrix multiplication
    def updateAllPlanePos(self):
        global result_y
        global result_x
        #get time displacement matrix
        dt = tm.getDt()
        result_x = np.matmul(dx_matrix,dt)
        result_y = np.matmul(result_x,line_matrix)



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
            x = velocity_x*(tm.global_time - t_0)+ x_0
            #calculate y
            y = slope*x + c
            return x,y
        except ZeroDivisionError:
            return x_0,y_0

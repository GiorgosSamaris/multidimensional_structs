class RouteGeneration:
    #Given the source and destination of the aircraft getDomain returns the x and y domain of the 
    #line equation
    def getDomain(self,a_coords,b_coords):

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


    def routeToEquation(self,start,end):
        try:
            #find slope of line eq
            slope = float((end[1] - start[1])/(end[0]-start[0]))#1 is for y and 0 is for x

            #find constant c of line eq
            c = float(end[1] - slope*end[0])
            return slope, c 
        except ZeroDivisionError:
            return None,None
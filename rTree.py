from telnetlib import NOOPT
from tkinter import N
from typing import ByteString
import numpy as np
import read_write_csv as rwc



# Create a node
class RTreeNode:
  def __init__(self, leaf=False):
    self.leaf = leaf
    #contains objects of type MinBoundingRectangle
    self.mbr = [] 
    #contains either objects of type RTreeNode or of type Object(if leaf)
    self.child = []

class MinBoundingRectangle:
    def __init__(self,x_thres,y_thres,t_thres):
        self.x = x_thres
        self.y = y_thres
        self.t = t_thres


class Object:
    def __init__(self,data):
        #calcData() maybe??
        self.mbr = data # = calcData() return 
        #data


# Tree
class RTree:
    def __init__(self, t):
        self.root = RTreeNode(True)
        self.M = t
        self.m = t//2
        


    def query(x_space,y_space,t_space):
            NOOPT

    # Insert node
    def insert(self,root,object):
        best_node = self.chooseLeaf(root,object)
        best_node.child.append(object)
        self.splitNode(best_node)


    def chooseLeaf(self,root,object) -> RTreeNode:
        if root.leaf:
            return root
        else:
            best_rect = self.bestCandidateRectangle(root,object)
            child = root.child[best_rect]
            return self.chooseLeaf(child,object)


    def bestCandidateRectangle(self, node:RTreeNode, object:Object) -> int:
        best_rect = np.zeros(3,dtype='int32')
        obj_mbr = object.mbr
        
        #init the prev_tup with infinite values 
        prev_tup = (float('inf'),float('inf'),float('inf'))
        
        for index,rect in enumerate(node.mbr):
            x_xceed = self.exceedCheck(rect.x,obj_mbr.x)
            y_xceed = self.exceedCheck(rect.y,obj_mbr.y)
            t_xceed = self.exceedCheck(rect.t,obj_mbr.t)
            curr_tup = (x_xceed,y_xceed,t_xceed)

            #creates a tuple and insert the boolean values of the following 
            #comparison
            

            for i, best_side in enumerate(curr_tup):
                #get the current best sides and insert them on the best_rect array
                if best_side < prev_tup[i]:
                    best_rect[i]=index

            
            prev_tup = curr_tup
            
        #check if there is a conflict for rectangle that needs least enlargement 
        occurences = np.bincount(best_rect)

        for i in occurences:
            if i < int(self.M)+1:
                check = True 
            else: check = False
        
        if check:
            #if yes resolve by smallest area
            best_area = float('inf')
            
            for rect_i in best_rect:
                n_area = self.calculateArea(node.mbr[rect_i])
                if n_area < best_area:
                    best_area = n_area
                    best_rect_i = rect_i
        else:
            best_rect_i = np.argmax(occurences)
        return best_rect_i



    def calculateArea(self,mbr:MinBoundingRectangle):
        area = 1
        for dimension in [mbr.x, mbr.y, mbr.t]:
            area *= abs(dimension[1]-dimension[0])
        return area


    def exceedCheck(self,rect_side:tuple, object_side:tuple) -> float:
        #get min and max value that describe a rect/object on one dimension
        rect_lower = rect_side[0]
        rect_upper = rect_side[1]
        object_lower = object_side[0]
        object_upper = object_side[1]


        #check in which side the new rectangle must be extended and by how much
        if object_lower < rect_lower:
            xceed = rect_lower-object_lower
        elif object_upper > rect_upper:
            xceed = object_upper - rect_upper
        else:
            xceed = 0
        return xceed


    def splitNode(self, node:RTreeNode):
        if(len(node.child) >= self.M):
            self.quadraticSplit(node)


    def quadraticSplit(self,node:RTreeNode):
        worst_pair = self.pickSeeds(node)

        pair_1 = RTreeNode()    
        pair_1.mbr.append(node.mbr[worst_pair[0]])    
        pair_1.child.append(node.child[worst_pair[0]])

        pair_2 = RTreeNode()
        pair_2.mbr.append(node.mbr[worst_pair[1]])    
        pair_2.child.append(node.child[worst_pair[1]])  

        del node.mbr[worst_pair]  
        del node.child[worst_pair]  

        if len(node.child) != 0:
            self.quadraticSplit(node)


    def pickSeeds(self,node:RTreeNode):
        worst_area = 0

        #find each possible combination of entries
        pair_comb = []
        for index_i, entry_i in enumerate(node.mbr):
            for index_j, entry_j in node.mbr[index_i+1:]:
                #pair_comb.append((entry_i,entry_j))
                #temporal MBR
                temp_tuple = []
                for dim_i,dim_j in entry_i,entry_j:
                    dim_domain = self.dimentionExtension(dim_i,dim_j)
                    temp_tuple.append(dim_domain)


                #calculate the area of each rectangle containing the pair
                #combinations        
                area_total = self.calculateArea(temp_tuple)
                area_i = self.calculateArea(entry_i)
                area_j = self.calculateArea(entry_j)
                d = area_total - area_i - area_j
                if d > worst_area:
                    worst_area = d
                    worst_pair = (index_i,index_j)
        return worst_pair

    def pickNext(self,node:RTreeNode):
         

    def dimentionExtension(self,curr_dim,added_dim):
        curr_lower = curr_dim[0]
        curr_upper = curr_dim[1]
        added_lower = added_dim[0]
        added_upper = added_dim[1]

        if curr_lower < added_lower:
            domain_min = curr_lower
        else:
            domain_min = added_lower


        if curr_upper < added_upper:
            domain_max = added_upper
        else:
            domain_max = curr_upper

        return (domain_min,domain_max)
        

def main():
    r = RTree(4)
    test_node = RTreeNode(False)
    mbr_1 = MinBoundingRectangle(x_thres=[2,8], y_thres=[1,5], t_thres=[1,3])
    mbr_2 = MinBoundingRectangle(x_thres=[3,10], y_thres=[5,9], t_thres=[1,3])
    mbr_3 = MinBoundingRectangle(x_thres=[8,14], y_thres=[2,7], t_thres=[1,3])
    mbr_4 = MinBoundingRectangle(x_thres=[10,13], y_thres=[6,11], t_thres=[1,3])
    obj_mbr = MinBoundingRectangle(x_thres=[14,15], y_thres=[13,14], t_thres=[1,3])
    n_obj = Object(obj_mbr)
    
    test_node.mbr.append(mbr_1)
    test_node.mbr.append(mbr_2)
    test_node.mbr.append(mbr_3)
    test_node.mbr.append(mbr_4)
    
    best = r.bestCandidateRectangle(test_node,n_obj)
    print(best)

if __name__ == '__main__':
  main()
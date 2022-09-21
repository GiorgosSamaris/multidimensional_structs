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
        self.mbr # = calcData() return 
        #data


# Tree
class RTree:
    def __init__(self, t):
        self.root = RTreeNode(True)
        self.t = t
        

      # Insert node

    def query(x_space,y_space,t_space):
            NOOPT

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


    



    def bestCandidateRectangle(self,node:RTreeNode,object:MinBoundingRectangle) -> int:
        best_rect = np.zeros(3)

        #init the prev_tup with infinite values 
        prev_tup = (float('inf'),float('inf'),float('inf'))
        
        for index,rect in enumerate(node.mbr):
            x_xceed = self.exceedCheck(rect.x,object.x)
            y_xceed = self.exceedCheck(rect.y,object.y)
            t_xceed = self.exceedCheck(rect.t,object.t)
            curr_tup = (x_xceed,y_xceed,t_xceed)

            #creates a tuple and insert the boolean values of the following 
            #comparison
            bool_tup = curr_tup < prev_tup

            prev_tup = curr_tup
            cur_v_index = 0
            for i,loc_best in enumerate(bool_tup):

                #get the current best sides and insert them on the best_rect array
                if loc_best:
                    best_rect[i]=index

            
        #check if there is a conflict for rectangle that needs least enlargement 
        best_candidates = np.bincount(best_rect).argmax() 
        if len(best_candidates) > 1:
            #if yes resolve by smallest area
            best_area = float('inf')
            best_rect = 0
            for rect_i in best_rect:
                n_area = self.calculateArea(rect_i)
                if n_area < best_area:
                    best_area = n_area
                    best_rect = rect_i
        else:
            best_rect = best_candidates
        return best_rect



    def calculateArea(self,rect_dimensions):
        area = 1
        for dimension in rect_dimensions:
            area *= abs(dimension[1]-dimension[0])
        return area


    def exceedCheck(self,rect_side:tuple,object_side:tuple) -> float:
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
        if(len(node.child) >= self.t):
            self.quadraticSplit(node)
        
    def quadraticSplit(self,node):
        self.pickSeeds(node)    

    def pickSeeds(self,node:RTreeNode):
        worst_area = 0

        
        #find each possible combination of entries
        pair_comb = []
        for index,entry_i in enumerate(node.mbr):
            for entry_j in node.mbr[index+1:]:
                #pair_comb.append((entry_i,entry_j))
                #temporal MBR
                temp_tuple = []
                for dim_i,dim_j in entry_i,entry_j:
                    dim_domain = self.dimentionExtension(dim_i,dim_j)
                    temp_tuple.append(dim_domain)
                temp_MBR = MinBoundingRectangle(temp_tuple[0],temp_tuple[1],temp_tuple[2])
            
        #calculate the area of each rectangle containing the pair
        #combinations
         

    def dimentionExtension(self,curr_dim,added_dim) -> tuple(float,float):
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
    B = RTree(3)
    read = rwc.ReadWriteCSV()
  

  #B.print_tree(B.root)
#
  #if B.search_key(8) is not None:
  #  print("\nFound")
  #else:
  #  print("\nNot Found")


if __name__ == '__main__':
  main()
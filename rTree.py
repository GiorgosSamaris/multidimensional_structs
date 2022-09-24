import copy
import re
from telnetlib import NOOPT
from tkinter import N
from typing import ByteString
import numpy as np
import read_write_csv as rwc



# Create a node
class RTreeNode:
  def __init__(self, leaf=False, parent = None):
    #is true when the node is a leaf
    self.leaf = leaf
    #pointer to parent node
    self.parent = None
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
        


    # Insert node
    def insert(self,mbr):
        #get leaf to insert new object
        best_node = self.chooseLeaf(self.root,mbr)
        L=best_node
        LL=None
        best_node.mbr.append(mbr)
        split_performed = 0
        
        #if node's entries exceed the maximum val M then call splitNode()
        if len(best_node.mbr) > self.M:
            print("split occured")
            L,LL = self.quadraticSplit(best_node)
            print("group 1 size"+str(len(L.mbr)))
            print("group 2 size"+str(len(LL.mbr)))
            split_performed = 1
        
        self.adjustTree(L,LL)  

        if L.parent == None and split_performed == 1:
            #if root split create new root
            self.root = RTreeNode() 
            self.root.child = L 
            self.root.child = LL 
            L.parent = self.root   
            LL.parent = self.root   
            print("new root created")



    def chooseLeaf(self,root,object) -> RTreeNode:
        if root.leaf:
            return root
        else:
            best_rect = self.bestCandidateRectangle(root,object)
            child = root.child[best_rect]
            return self.chooseLeaf(child,object)


    def bestCandidateRectangle(self, node:RTreeNode, object:MinBoundingRectangle) -> int:
        best_rect = np.zeros(3,dtype='int32')
        obj_mbr = object
        
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


    def quadraticSplit(self,node:RTreeNode):
        worst_pair = self.pickSeeds(node)

        group_1 = RTreeNode()    
        group_1.mbr.append(node.mbr[worst_pair[0]])    
        #group_1.child.append(node.child[worst_pair[0]])

        group_2 = RTreeNode()
        group_2.mbr.append(node.mbr[worst_pair[1]])    
        
        #group_2.child.append(node.child[worst_pair[1]])  

        del node.mbr[worst_pair[0]]  
        del node.mbr[worst_pair[1]]  
        #del node.child[worst_pair]  

        while len(node.mbr) > 0:
            
            
            
            
            if len(group_1.mbr) < self.m and (len(group_1.mbr) + len(node.mbr)) == self.m:
                #group_1.child.append(node.child)
                group_1.mbr.extend(node.mbr)
                
                break

            elif len(group_2.mbr) < self.m and len(group_2.mbr) + len(node.mbr) == self.m:
                #group_1.child.append(node.child)
                group_2.mbr.extend(node.mbr)
                
                break
            
            else:
                next_pick = self.pickNext(node,group_1,group_2)
                
                tmp_node = RTreeNode()

                #calc total mbrs of groups
                min_1, max_1 = self.findMinMax(group_1)
                mbr_1 = MinBoundingRectangle([min_1[0],max_1[0]],
                [min_1[1],max_1[1]],[min_1[2],max_1[2]])


                min_2, max_2 = self.findMinMax(group_2)
                mbr_2 = MinBoundingRectangle([min_2[0],max_2[0]],
                [min_2[1],max_2[1]],[min_2[2],max_2[2]])

                tmp_node.mbr.append(mbr_1)
                tmp_node.mbr.append(mbr_2)
                
                
                best_group = self.bestCandidateRectangle(tmp_node,node.mbr[next_pick])
               
                if best_group == 0:
                    #group_1.child.append(node.child)
                    mbr = node.mbr.pop(next_pick)
                    
                    group_1.mbr.append(mbr)    
                else:
                    #group_1.child.append(node.child)
                    group_1.mbr.append(node.mbr.pop(next_pick))
                    
        
        return group_1,group_2


    def pickSeeds(self,node:RTreeNode):
        worst_area = 0

        #find each possible combination of entries
        pair_comb = []
        for index_i, entry_i in enumerate(node.mbr):
            for index_j, entry_j in enumerate(node.mbr[index_i+1:]):
                
                temp_node = RTreeNode()
                temp_node.mbr.append(entry_i)
                temp_node.mbr.append(entry_j)
                min_1, max_1 = self.findMinMax(temp_node)
    
                area_mat_1 = max_1 - min_1
                area_total = area_mat_1[0] * area_mat_1[1] * area_mat_1[2]

                #calculate the area of each rectangle containing the pair
                #combinations        
        
                area_i = self.calculateArea(entry_i)
                area_j = self.calculateArea(entry_j)
                d = area_total - area_i - area_j
                if d > worst_area:
                    worst_area = d
                    worst_pair = (index_i,index_j)
        return worst_pair


    def pickNext(self,node:RTreeNode,group_1:RTreeNode, group_2:RTreeNode)->int:
        

        #calculate group_1 volume
        min_1, max_1 = self.findMinMax(group_1)
    
        area_mat_1 = max_1 - min_1
        area_1 = area_mat_1[0] * area_mat_1[1] * area_mat_1[2]


        #calculate group_2 volume
        min_2, max_2 = self.findMinMax(group_2)
        
        area_mat_2 = max_2 - min_2
        area_2 = area_mat_2[0] * area_mat_2[1] * area_mat_2[2]

        worst_dif = 0
        next_pick = 0
        tmp_node_1 = RTreeNode()
        tmp_node_2 = RTreeNode()

        for index, entry in enumerate(node.mbr):
            #calculate group_1 volume including the new element
            tmp_node_1 =copy.deepcopy(group_1)
            tmp_node_1.mbr.append(entry)

            tmp_min_1, tmp_max_1 = self.findMinMax(tmp_node_1)
            tmp_area_mat_1 = tmp_max_1 - tmp_min_1
            tmp_area_1 = tmp_area_mat_1[0]*tmp_area_mat_1[1]*tmp_area_mat_1[2]


            #calculate group_2 volume including the new element
            tmp_node_2 = copy.deepcopy(group_2)
            tmp_node_2.mbr.append(entry)

            tmp_min_2, tmp_max_2 = self.findMinMax(tmp_node_2)
            tmp_area_mat_2 = tmp_max_2 - tmp_min_2
            tmp_area_2 = tmp_area_mat_2[0]*tmp_area_mat_2[1]*tmp_area_mat_2[2]

            d_1 = tmp_area_1 - area_1
            d_2 = tmp_area_2 - area_2

            dif = abs(d_2 - d_1)
            if worst_dif < dif:
                worst_dif = dif
                next_pick = index
             
        return next_pick
        
            
    def findMinMax(self,node:RTreeNode):
        min_ar = np.full(3,float('inf'),dtype='float32')
        max_ar = np.zeros(3,dtype='float32')
        for i,entry in enumerate(node.mbr):
            if(i==0):
                min_ar = np.array([entry.x[0],entry.y[0],entry.t[0]])
            min_temp = np.array([entry.x[0],entry.y[0],entry.t[0]])
            max_temp = np.array([entry.x[1],entry.y[1],entry.t[1]])
           
            min_bool = min_ar > min_temp
            
            max_bool = max_ar < max_temp

            min_ar = min_ar * ~min_bool + min_temp * min_bool
            max_ar = max_ar * ~max_bool + max_temp * max_bool
        return min_ar,max_ar


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
        

    def adjustTree(self,L:RTreeNode,LL:RTreeNode=None):
        if L.parent == None:
            return


    def updateParentMBR(self, node:RTreeNode):
        for entry in node:

def main():
    r = RTree(4)
    
    test_node = RTreeNode(False)
    mbr_1 = MinBoundingRectangle(x_thres=[2,8], y_thres=[1,5], t_thres=[1,3])
    mbr_2 = MinBoundingRectangle(x_thres=[3,10], y_thres=[5,9], t_thres=[1,3])
    mbr_3 = MinBoundingRectangle(x_thres=[8,14], y_thres=[2,7], t_thres=[1,3])
    mbr_4 = MinBoundingRectangle(x_thres=[10,13], y_thres=[6,11], t_thres=[1,3])
    obj_mbr = MinBoundingRectangle(x_thres=[14,15], y_thres=[13,14], t_thres=[1,3])
    n_obj = Object(obj_mbr)
    
    r.insert(mbr_1)
    r.insert(mbr_2)
    r.insert(mbr_3)
    r.insert(mbr_4)
    r.insert(obj_mbr)
    
    

if __name__ == '__main__':
  main()
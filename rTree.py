import copy
from multiprocessing import parent_process
import re
from telnetlib import NOOPT
from tkinter import N
from typing import ByteString, overload
import numpy as np
import planeGeneration as plane



# Create a node
class RTreeNode:
  def __init__(self, leaf=False, p_index = None):
    #is true when the node is a leaf
    self.leaf = leaf
    #pointer to parent node
    self.parent = None

    self.p_index = p_index
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
    def __init__(self,data,mbr:MinBoundingRectangle):
        self.mbr = mbr
        self.data = data


# Tree
class RTree:
    def __init__(self, t):
        self.root = RTreeNode(True)
        self.M = t
        self.m = t//2
        


    # Insert node
    def insert(self,obj:Object):
        mbr = obj.mbr
        
        #get leaf to insert new object
        best_node = self.chooseLeaf(self.root,mbr)
        L = best_node
        LL = None
        best_node.mbr.append(mbr)
        
        best_node.child.append(obj)
        split_performed = 0
        
        #if node's entries exceed the maximum val M then call splitNode()
        if len(best_node.mbr) > self.M:
            
            L,LL = self.quadraticSplit(best_node)
        

            split_performed = 1
        
        
        N,NN, split_performed = self.adjustTree(L,LL,split_performed)  

        #root splitted due to split propagation
        if split_performed == 1:
            #if root split create new root
            
            n_root = RTreeNode()
            self.root = n_root 
            self.root.child.append(N) 
            self.root.child.append(NN) 

            N.parent = self.root   
            NN.parent = self.root   
            
            min,max = self.findMinMax(N)
            parent_node = N.parent
            mbr = MinBoundingRectangle([min[0],max[0]],[min[1],max[1]],
            [min[2],max[2]])
            parent_node.mbr.append(mbr)

            min,max = self.findMinMax(NN)
            parent_node = NN.parent
            mbr = MinBoundingRectangle([min[0],max[0]],[min[1],max[1]],
            [min[2],max[2]])
            parent_node.mbr.append(mbr)
            
            



    def chooseLeaf(self,root:RTreeNode,object) -> RTreeNode:
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
            if i < 2:
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
        

        #new nodes are leaves only if the node that is being split
        #is a leaf
        leaf = node.leaf

        group_1 = RTreeNode(leaf)    
        group_1.mbr.append(node.mbr.pop(worst_pair[0]))    
        group_1.child.append(node.child.pop(worst_pair[0]))

        group_2 = RTreeNode(leaf)
        group_2.mbr.append(node.mbr.pop(worst_pair[1]-1))    
        group_2.child.append(node.child.pop(worst_pair[1]-1))  

         

        while len(node.mbr) > 0:
    
            if len(group_1.mbr) < self.m and (len(group_1.mbr) + len(node.mbr)) == self.m:
                group_1.child.extend(node.child)
                group_1.mbr.extend(node.mbr)
                
                break

            elif len(group_2.mbr) < self.m and len(group_2.mbr) + len(node.mbr) == self.m:
                
                group_2.child.extend(node.child)
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
                    group_1.child.append(node.child.pop(next_pick))
                    mbr = node.mbr.pop(next_pick)
                    
                    group_1.mbr.append(mbr)    
                else:
                    group_1.child.append(node.child.pop(next_pick))
                    group_1.mbr.append(node.mbr.pop(next_pick))

        
        group_2.parent = node.parent

       
        node.mbr = group_1.mbr
        node.child = group_1.child
        
        return node,group_2


    def pickSeeds(self,node:RTreeNode):
        worst_area = 0

        #find each possible combination of entries
        
        for index_i, entry_i in enumerate(node.mbr):
          
            for index_j in range(index_i+1,len(node.mbr)):
                entry_j = node.mbr[index_j]
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
        

    def adjustTree(self,L:RTreeNode,LL:RTreeNode,split_occured = 0):

        if L.parent == None:
            return L,LL,split_occured
        
        
        self.updateParentMBR(L)
        if split_occured == 1:
            
            parent = L.parent
            parent.child.append(LL)

            #caclulate new mbr
            min_2, max_2 = self.findMinMax(LL)
            mbr_2 = MinBoundingRectangle([min_2[0],max_2[0]],
            [min_2[1],max_2[1]],[min_2[2],max_2[2]])
            parent.mbr.append(mbr_2)

            if len(parent.child)>self.M:
                
                N,NN = self.quadraticSplit(parent)
                
                return self.adjustTree(N,NN,1)
        return self.adjustTree(L.parent,None,0)
                

    def updateParentMBR(self, node:RTreeNode):
        for i,e in enumerate(node.parent.child):
            min,max = self.findMinMax(e)
            
            mbr = node.parent.mbr[i]
            mbr.x = [min[0],max[0]]
            mbr.y = [min[1],max[1]]
            mbr.t = [min[2],max[2]]


    def search(self, root:RTreeNode, mbr:MinBoundingRectangle):
        qualifying_rec = []
        
        if root.leaf==False:
            
            for i,e in enumerate(root.child):
                if self.overlaps(mbr,root.mbr[i]):
                    
                    qualifying_rec.extend(self.search(e,mbr))
        else:
            for i,e in enumerate(root.child):
                if self.overlaps(root.mbr[i],mbr):
                    
                    qualifying_rec.append(e)
        return qualifying_rec      


    def overlaps(self,mbr_1:MinBoundingRectangle,mbr_2:MinBoundingRectangle):
        x_overlap = True
        y_overlap = True
        t_overlap = True
        if mbr_1.x[1] < mbr_2.x[0] or mbr_2.x[1]<mbr_1.x[0]:
            x_overlap = False

        if mbr_1.y[1] < mbr_2.y[0] or mbr_2.y[1]<mbr_1.y[0]:
            y_overlap = False

        if mbr_1.t[1] < mbr_2.t[0] or mbr_2.t[1]<mbr_1.t[0]:
            t_overlap = False
        
        return x_overlap and y_overlap and t_overlap
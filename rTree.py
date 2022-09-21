from telnetlib import NOOPT
from tkinter import N
from typing import ByteString
import numpy as np
import read_write_csv as rwc

dif = lambda x:tuple : abs(x[1]-x[0])

# Create a node
class BTreeNode:
  def __init__(self, leaf=False):
    self.leaf = leaf
    self.mbr = []
    self.child = []

class Object:
    def __init__(self,x_thres,y_thres,t_thres):
        self.x = x_thres
        self.y = y_thres
        self.t = t_thres

# Tree
class RTree:
    def __init__(self, t):
        self.root = BTreeNode(True)
        self.t = t
        

      # Insert node

    def query(x_space,y_space,t_space):
            NOOPT

    def chooseLeaf(self,root,new_tup) -> BTreeNode:
        if root.leaf:
            return root
        else:
            best_rect = self.bestCandidateRectangle(root,new_tup)
            child = root.child[best_rect]
            return self.chooseLeaf(child,new_tup)


    def bestCandidateRectangle(self, node:BTreeNode, object):
        cand_rect_area = []
        object_area = object.x * object.y * object.t
        for rect in node.child:
            x_side = rect.x[1] - rect.x[0]
            y_side = rect.y[1] - rect.y[0]
            t_side = rect.t[1] - rect.t[0]
        
            cand_rect_area.append(area)



    def bestCandidateRectangle(self,node,new_tup):
        best_rect = np.zeros(3)
        prev_tup = (float('inf'),float('inf'),float('inf'))
        cur_k_index = 0
        for nd in node.keys:
            x_xceed = self.exceedCheck(nd[0],new_tup[0])
            y_xceed = self.exceedCheck(nd[1],new_tup[1])
            t_xceed = self.exceedCheck(nd[2],new_tup[2])
            curr_tup = (x_xceed,y_xceed,t_xceed)
            bool_tup = curr_tup < prev_tup
            prev_tup = curr_tup
            cur_v_index = 0
            for i in bool_tup:
                if i == True:
                    best_rect[cur_v_index]=cur_k_index
                cur_v_index +=1
            cur_k_index +=1
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


    def exceedCheck(self,bound,val):
        lower = bound[0]
        upper = bound[1]
        if val < lower:
            xceed = lower-val
        elif val > upper:
            xceed = val - upper
        else:
            xceed = 0
        return xceed


    def splitNode(self, node):
        NOOPT
        
    def pickSeeds(self,node):
        NOOPT
    


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
from tkinter import N
from typing import ByteString
import numpy as np
import read_write_csv as rwc

# Create a node
class BTreeNode:
  def __init__(self, leaf=False):
    self.leaf = leaf
    #keys are represented by a tuple of 3 tuples
    self.keys = []
    self.child = []


# Tree
class BTree:
    def __init__(self, t):
        self.root = BTreeNode(True)
        self.t = t
        x_tup = (None,None)
        y_tup = (None,None)
        t_tup = (None,None)
        k_tup = (x_tup,y_tup,t_tup)

      # Insert node

    def chooseLeaf(self,root,new_tup):
        if root.leaf:
            return root
        else:
            best_rect = self.bestCandidateRectangle(root,new_tup)
            child = root.child[best_rect]
            return self.chooseLeaf(child,new_tup)



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




    def insert(self, key_tuple):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            temp = BTreeNode()
            self.root = temp
            temp.child.insert(0, root)
            self.split_child(temp, 0)
            self.insert_non_full(temp, key_tuple)
        else:
            self.insert_non_full(root, key_tuple)

      # Insert nonfull
    def insert_non_full(self, x, n_tuple):
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append((None, None))
            while i >= 0 and self.compareKey(x.keys[i],n_tuple):
                x.keys[i + 1] = x.keys[i]
                i -= 1
                x.keys[i + 1] = n_tuple
        else:
            while i >= 0 and self.compareKey(x.keys[i],n_tuple):
                i -= 1
            i += 1
            if len(x.child[i].keys) == (2 * self.t) - 1:
                self.split_child(x, i)
            if n_tuple > x.keys[i][0]:
                i += 1
            self.insert_non_full(x.child[i], n_tuple)

      # Split the child
    def split_child(self, x, i):
        t = self.t
        y = x.child[i]
        z = BTreeNode(y.leaf)
        x.child.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        z.keys = y.keys[t: (2 * t) - 1]
        y.keys = y.keys[0: t - 1]
        if not y.leaf:
            z.child = y.child[t: 2 * t]
            y.child = y.child[0: t - 1]

    

    # Print the tree
    def print_tree(self, x, l=0):
        print("Level ", l, " ", len(x.keys), end=":")
        for i in x.keys:
            print(i, end=" ")
        print()
        l += 1
        if len(x.child) > 0:
            for i in x.child:
                self.print_tree(i, l)

    # Search key in the tree
    def search_key(self, k, x=None):
        if x is not None:
            i = 0
            while i < len(x.keys) and k > x.keys[i][0]:
                i += 1
            if i < len(x.keys) and k == x.keys[i][0]:
                return (x, i)
            elif x.leaf:
                return None
            else:
                return self.search_key(k, x.child[i])

        else:
            return self.search_key(k, self.root)


    def compareKey(self,key_tuple,new_tuple):
        if new_tuple[0] in range(key_tuple[0]) and new_tuple[1] in range(key_tuple[1]) and new_tuple[2] in range(key_tuple[2]):
            return True
        else:
            return False


def main():
    B = BTree(3)
    read = rwc.ReadWriteCSV()
  

  #B.print_tree(B.root)
#
  #if B.search_key(8) is not None:
  #  print("\nFound")
  #else:
  #  print("\nNot Found")


if __name__ == '__main__':
  main()
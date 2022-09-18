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
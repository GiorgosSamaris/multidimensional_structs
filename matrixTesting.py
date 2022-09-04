import numpy as np
import random as rand
import time


epoch = time.time()
arr_1 = np.ones((100000000,2))

print(arr_1)

arr_rand = np.random.randint(10,size=(len(arr_1),1))



#print("//////////Running for loop configuration//////////")
#current = time.time() - epoch
#for i ,j in zip(arr_1,arr_rand):
#    i[1]=j
#current = time.time() - epoch - current
#print(arr_1)
#
#
#print("time neeed to update: ",current)
#


print("//////////Running delete/append configuration//////////")
current = time.time() - epoch

arr_1 = np.delete(arr_1,1,axis=1)


arr_1 = np.hstack([arr_1,arr_rand])
current = time.time() - epoch - current

print(arr_1)
print("time neeed to update: ",current)
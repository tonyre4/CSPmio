import numpy as np
import itertools as it

#global cuts

cuts = [10. , 10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.
                ,10.,10.,10.,10.,10., 10., 10., 10., 10., 10., 10., 10., 10. ,11.
                ,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.]

a = it.permutations(cuts,5)

for i in list(a):
    print (a)



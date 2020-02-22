import numpy as np
from scipy.optimize import minimize,brute
from pulp import *

#cuts = np.array([10. , 10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.
#                ,10.,10.,10.,10.,10., 10., 10., 10., 10., 10., 10., 10., 10. ,11.
#                ,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.])
cuts = np.array([2.4 , 1.1,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.
                ,10.,12.5,10.,10.,10., 10., 10., 10., 10., 10., 10., 10., 10. ,11.
                ,1.,1.,1.,19.19,1.,1.,1.,1.,1.,1.,19.19,11.6,45.3,64.3,7.4,88.2,4.4,55.5,9.2,1.4,5.6,33.6,77.5,
                77.5,2.4,4.4,9.2,1.4,5.6,5.6,5.6,5.6,5.6,19.19,1.1,1.,1.1,1.1,10.1,10.1,10.1,10.1,10.1,10.1,10.1,88.2,88.2,88.2,8.2,88.2,88.2])

cuts[::-1].sort()


global measUn,measCnt

measUn, measCnt = np.unique(cuts, return_counts=True)
measCnt.astype(np.uint)
s_size = 100.


measUn = np.flip(measUn)
measCnt = np.flip(measCnt)






class cutSolver:

    def __init__(me,measures,counters,stockSize):
        me.orders = []
        me.ordersSimple = []
        me.stS = stockSize
        me.measures = measures
        me.counters = counters.astype(np.uint)
        me.getOrders()
        #print(me.orders)
        me.printOrders()


    def getBest(me):
        prob = LpProblem("Cut_problem",LpMaximize)

        Xs = []

        for i,c in enumerate(me.counters):
            Xi=LpVariable("X{0:05d}".format(i),0,int(c),LpInteger)
            Xs.append(Xi)
            prob.objective += Xi*me.measures[i]

        c = prob.objective

        prob.objective = prob.objective == s_size

        prob += s_size - (c)  >= 0. , "No menor que cero"
        prob.solve()


        XXX = np.ones(me.measures.shape[0])

        for i,v in enumerate(prob.variables()):
            #print(v.name, "=", v.varValue)
            try:
                XXX[i] = v.varValue
            except:
                pass

        return np.array(XXX,np.uint)

    def printOrders(me):

        print("Imprimiendo ordenes...")

        for i,o in enumerate(me.ordersSimple):
            print("Orden %d:" % (i+1))
            print("Forma del corte:\n\t",end="")
            print(o[0])
            print("x%d ve" % o[1],end="")
            if o[1]==1:
                print("z",end="\t")
            else:
                print("ces",end="\t")

            print("Sobrante: %f" % o[2])

            print("-"*70)
            print("")




    def getOrders(me,p=False):
        while np.sum(me.counters)>0:
            bs = me.getBest()
            bs = bs.astype(np.uint)

            div = me.counters/bs
            div = div[~np.isnan(div)]

            times = int(np.min(div))

            if p:
                print("Best:")
                print(bs)
                print("Counters:")
                print(me.counters)
                print("Iguales:", times)

            oor = []
            for n,i in enumerate(bs):
                for ii in range(i):
                    oor.append(me.measures[n])


            for i in range(times): # genera las ordenes
                me.orders.append(oor)

            me.ordersSimple.append([oor,times,me.stS-np.sum(np.array(oor))])

            rest = bs*times
            #rest = rest.astype(np.uint)

            me.counters -= rest
            app = np.sum(np.array(oor))
            if p:
                print("Resta:")
                print(rest)
                print("Despues de resta:")
                print(me.counters)
                print("Aprovechado:")
                print(app)
                print("Scrap:")
                print(me.stS-app)
                print("")


cutSolver(measUn,measCnt,s_size)

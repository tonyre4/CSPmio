import numpy as np
from scipy.optimize import minimize,brute

#cuts = np.array([10. , 10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.
#                ,10.,10.,10.,10.,10., 10., 10., 10., 10., 10., 10., 10., 10. ,11.
#                ,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.])
cuts = np.array([2.4 , 1.1,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.
                ,10.,12.5,10.,10.,10., 10., 10., 10., 10., 10., 10., 10., 10. ,11.
                ,1.,1.,1.,19.19,1.,1.,1.,1.,1.,1.,19.19,11.6,45.3,64.3,7.4,88.2,4.4,55.5,9.2,1.4,5.6,33.6,77.5])

cuts[::-1].sort()

global measUn,measCnt
measUn, measCnt = np.unique(cuts, return_counts=True)
measCnt.astype(np.uint)

def calc(x, *params):
    measures, st, p = params
    #print(x.shape)
    #print(measures.shape)

    s = x*measures
    su = np.sum(s)
    e = 100-su

    if p:
        print("Medidas:")
        print(measures)
        print("Cortes:")
        print(x)
        print("Por corte:")
        print(s)
        print("Suma:")
        print(su)
        print("err:")
        print(e)
        print(" ")

    if e<0:
        e=1000
    return e

class cutSolver:

    def __init__(me,measures,counters,stockSize):
        me.orders = []
        me.stS = stockSize
        me.measures = measures
        me.counters = counters
        me.getOrders()
        print(me.orders)


    def getBest(me):
        ranges = []
        for i in me.counters:
            ranges.append(slice(0,i+1,1))
        ranges = tuple(ranges)
        print(ranges)
        return brute(calc,ranges, args=(me.measures,me.stS,False), disp=True, finish= None)

    def getOrders(me):
        while np.sum(me.counters)>0:
            bs = me.getBest()
            bs = bs.astype(np.uint)
            print("Best:")
            print(bs)
            print("Counters:")
            print(me.counters)
            times = int(np.min(me.counters/bs))
            print("Iguales:", times)

            oor = []
            for n,i in enumerate(bs):
                for ii in range(i):
                    oor.append(me.measures[n])


            for i in range(times): # genera las ordenes
                me.orders.append(oor)

            rest = bs*times
            rest = rest.astype(np.uint)

            print("Resta:")
            print(rest)
            me.counters -= rest
            print("Despues de resta:")
            print(me.counters)

            print("Aprovechado:")
            app = np.sum(np.array(oor))
            print(app)
            print("Scrap:")
            print(me.stS-app)
            print("")

print(measUn)
print(measCnt)

cutSolver(measUn,measCnt,100.)

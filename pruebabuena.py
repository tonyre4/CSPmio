import numpy as np
from scipy.optimize import minimize,brute
from pulp import *


measUn = np.array([81.,84.,84.1,75.75,34.,46.5,79.5,79.,79.7,82.5,72.75,96.25,88.,93.875,83.5,80.,84.5,10.25,100.,93.,91.875,92.75])
measCnt = np.array([2,27,24,23,11,45,48,48,48,41,54,28,5,23,46,31,33,31,32,22,17,40])

#print(measUn.shape[0])

s_size = 192.

measUn = np.flip(measUn)
measCnt = np.flip(measCnt)

print("**Reporte de solicitud de cortes**")
print("Numero de parte: 68-9306-40")
print("-"*50)
print("Tamaño del corte:     Cantidad de cortes:")

for a,b in zip(measUn,measCnt):
    print("%.3f" % (a) + "\t"*8 + str(b))

print("#"*50)



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

    def printRequ(me):
        print("**Reporte de requisicion**")
        print("-"*70)
        print("Numero de parte: 68-9306-40")
        print("-"*70)
        
        num_tot = 0

        for i,o in enumerate(me.ordersSimple):
            num_tot += o[1]

        print("Total de Louvers:")
        print("\t" + str(num_tot))
        print("Total ft:")
        print("\t" + str(me.stS*num_tot))
        print("-"*70)
        print("")

    def printOrders(me):

        me.printRequ()
        print("#"*50)
        print("**Reporte de corrida**")


        prom_perc = 0.0
        prom_perc2 = 0.0
        num_tot = 0

        st = 0.0
        stp = 0.0


        for i,o in enumerate(me.ordersSimple):
            print("Orden %d:" % (i+1))
            print("Forma del corte:\n\t",end="")
            print(o[0])
            print("x%d ve" % o[1],end="")
            num_tot += o[1]
            if o[1]==1:
                print("z",end="\t")
            else:
                print("ces",end="\t")

            print("\t\tSobrante: %f = %f" % (o[2], o[3]), "%")

            prom_perc += o[3]*o[1]
            prom_perc2 += o[2]*o[1]
            st += o[2]
            stp += o[3]

            print("-"*70)
            print("")


        prom_perc /= num_tot
        prom_perc2 /= num_tot


        print("Sobrante promedio (por louver): %f"%(prom_perc), end = "")
        print("%")
        print("Sobrante promedio (por louver) en pulgadas: %f" % prom_perc2)

        print("Sobrante acumulado en %d louvers en pulgadas: %f -->  %f louvers" % (num_tot,st,st/me.stS))


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

            scrap = me.stS-np.sum(np.array(oor))
            perc = scrap*100./me.stS

            me.ordersSimple.append([oor,times,scrap,perc])

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

import numpy as np
from scipy.optimize import minimize,brute
from pulp import *
from Rmaker import *


class sortHandler:
    def __init__(me,st_size,cuts,num_prt):
        me.np = num_prt
        me.stS = st_size
        me.cuts = cuts

        me.meas = me.cuts[:,0]
        me.cntrs = me.cuts[:,1]

        me.printCutRep(P=True)
        me.solv = cutSolver(num_prt,me.meas,me.cntrs,me.stS)
    

    def printCutRep(me,P=False):

        s = "**Reporte de solicitud de cortes**\n"
        s += "Numero de parte: %s\n" % me.np
        s += str("-"*50) + "\n"
        s += "Tamaño del corte:     Cantidad de cortes:\n"

        for a,b in zip(me.meas,me.cntrs):
            s += "%.3f" % (a) + "\t"*8 + str(b) + "\n"

        s += str("#"*50) + "\n"

        if P:
            print(s)

        me.cutR = s



class cutSolver:

    def __init__(me,num_prt,measures,counters,stockSize):
        me.num_prt = num_prt
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

        prob.objective = prob.objective == me.stS

        prob += me.stS - (c)  >= 0. , "No menor que cero"
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

    def pdfRun(me):
        cutReport(me.num_prt,me.ordersSimple,"./reports/")

    def printOrders(me):
        me.pdfRun()
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
        print("##"*25)
        print("\n\n")

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



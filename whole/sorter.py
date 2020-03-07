import numpy as np
from scipy.optimize import minimize,brute
from pulp import *
from Rmaker import *


class sortHandler:
    def __init__(me,st_size,cuts,num_prt,path_r):
        me.np = num_prt
        me.stS = st_size
        me.cuts = cuts
        me.pr = path_r

        me.meas = me.cuts[:,0]
        me.cntrs = me.cuts[:,1]

        #me.printCutRep(p=True)
        me.path_r = path_r
        me.solv = cutSolver(num_prt,me.meas,me.cntrs,me.stS,path_r)
    
    def getReq(me):
        return me.solv.getReq()


class cutSolver:

    def __init__(me,num_prt,measures,counters,stockSize,path_r):
        me.path_r = path_r
        me.num_prt = num_prt
        me.orders = []
        me.ordersSimple = []
        me.ordersForReport = []
        me.stS = stockSize
        me.measures = measures
        me.counters = counters.astype(np.uint)
        me.getOrders()
        me.printOrders()


    #Algorimtmo optimizador
    ########################
    ########################
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
            isScrap = (scrap>0)
            perc = scrap*100./me.stS
            percs = [x/me.stS for x in oor]

            me.ordersSimple.append([oor,times,scrap,perc])
            me.ordersForReport.append([oor,percs,isScrap,times,scrap,perc])

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

    ###########################################
    ###########################################
    
    ##Reportes
    def printRequ(me, p = False):
        num_tot = 0

        for i,o in enumerate(me.ordersSimple):
            num_tot += o[1]
        
        me.totLouv = num_tot
        me.ftTotLouv = num_tot*me.stS
        me.req = [me.totLouv,me.ftTotLouv]
        
        if p:
            print("**Reporte de requisicion**")
            print("-"*70)
            print("Numero de parte: 68-9306-40")
            print("-"*70)
            print("Total de Louvers:")
            print("\t" + str(num_tot))
            print("Total ft:")
            print("\t" + str(me.stS*num_tot))
            print("-"*70)
            print("")

    def getReq(me):
        try:
            return me.req
        except:
            me.printRequ()
            return me.req

    def pdfRun(me):
        cutReport(me.num_prt,me.ordersForReport,"./reports/")

    def printOrders(me,p = False, gr = True):
        me.printRequ()

        r = "#"*50 +"\n"
        r += "**Reporte de corrida**\n"
        r += "Numero de parte: %s\n" % me.num_prt
        r += "#"*50 +"\n"
        r += "#"*50 +"\n"

        #Inits
        prom_perc = 0.0
        prom_ft = 0.0
        num_tot = 0
        st = 0.0
        stp = 0.0

        sss = ""

        for i,o in enumerate(me.ordersSimple):
            prom_perc += o[3]*o[1]
            prom_ft += o[2]*o[1]
            st += o[2]
            stp += o[3]

        
            ss = "Patron %d:\n" % (i+1)
            ss += "Forma del corte:\n\t"
            ss += str(o[0]) + "\n"
            ss += "x%d ve" % o[1]

            if o[1]==1:
                ss += "z\t"
            else:
                ss += "ces\t"
            ss += "\t\tSobrante: %f = %f%%\n" % (o[2], o[3])
            ss += "-"*70 + "\n\n"

            sss += ss

            if p:
                print(ss)


        prom_perc /= me.totLouv
        prom_ft /= me.totLouv
        me.scrapLouvers = st/me.stS
        
        me.meanScrapPercent = prom_perc
        me.meanScrapft = prom_ft
        me.sumScrapft = st

        r += "Material: %d Louvers\nMaterial acumulado: %.2fin\n" % (me.totLouv,me.totLouv*me.stS)     

        #r += "Sobrante promedio (por louver): %f%%\n"%(me.meanScrapPercent)
        r += "Sobrante promedio (por louver) en pulgadas: %.2fin --> %.2f%%\n" % (me.meanScrapft, me.meanScrapPercent)

        r += "Sobrante acumulado en %d louvers: %.2fin -->  %.2f louvers\n" % (me.totLouv,me.sumScrapft,me.scrapLouvers)
        r += "#"*50 + "\n"

        r += sss

        if p:
            print(r)
        if gr:
            n_file = "%s%s_cutReport.txt" % (me.path_r, me.num_prt)
            with open(n_file,"w") as f:
                f.write(r)

        #me.pdfRun()




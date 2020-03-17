import numpy as np
from scipy.optimize import minimize,brute
from pulp import *
from Rmaker import *
import pandas as pd

class ordenes:
    def __init__(me,pers,num_prt):
        me.persianas = pers
        me.np = num_prt
        me.nps = me.np.split("-")
        me.color = me.nps[1]
        if me.nps[2]=="40":
            me.LouverLong = 192.
        else:
            me.LouverLong = 82.5

        me.ps = []
        me.slotCtr = 0

        for i,p in me.persianas.iterrows():
            me.ps.append(persiana(p,me.np))
        
        #me.computeCuts()

    def computeCuts(me):
        cuts = np.array(me.persianas.loc[:,["TrackWidthNumeric", "LouverQty"]])
        

        #agregando valances
        for p in me.ps:
            if p.Vbool:
                cuts = np.vstack([cuts,[p.getVW(),1]])
            else:
                if not p.Vbool is None:
                    print("ATENCIÓN!. El color del Valance de X no es el mismo que del louver. Este programa aún no está preparado para esta combinación!")
        

        #Valores de cortes ordenados
        twn = np.unique(cuts[:,0])
        #Obteniendo el total de cortes por cada medida
        meas = np.empty((0,2))
        for w in twn:
            s = np.sum(cuts[np.where(cuts[:,0]==w),1])
            meas = np.vstack([meas,[w,s]])

        #print("Cuts:")
        #print(cuts)
        #print("Unique")
        #print(twn)
        #print("Sum:")
        #print(meas)

        me.computedCuts = meas
        return meas

    def buscarCorte(me,corte):
        acaba = False

        for p in me.ps:
            if p.setCut(corte):
                if p.slot == -1:
                    p.slot = int(me.slotCtr%10)+1
                    p.car = int(me.slotCtr/10)+1
                    me.slotCtr += 1
                if p.RDY:
                    #print("Aqui termina la orden del slot ", p.slot," del carro ", p.car)
                    acaba = True
                me.slotternow.append(p.slot)
                break
        else:
            print("Error!, No se encontró el corte")
            exit()
        #print("Corte:",corte)
        #print("Slot:", p.slot)
        #print("Carro:", p.car)
        return acaba

    def printReport2(me, optimizado):
        opti = optimizado.copy()

        for ip,p in enumerate(me.ps):
            print("Computando orden %d" % ip)
            while not p.RDY:
                ##Encontrar el mejor de todos los cortes que puede llenar el pedido
                maxoc = 0
                maxind = None
                for ii,o in enumerate(opti):
                    if o["veces"]==0:
                        continue
                    if p.Lmeas in o["cortes"]:
                        cnt = o["cortes"].count(p.Lmeas)
                        if maxoc<cnt:
                            maxind = ii
                ##Ya encontrado ahora hay que ir bajando las veces en cada corte
                try:
                    mc = opti[maxind]
                except:
                    print(p.Lqty,p.Lqtymade)
                    exit()

                for i in range(mc["veces"]):
                    for c in mc["cortes"]:
                        if c == p.Lmeas: #Si es un corte de la persiana
                            p.Lqtymade += 1
                            p.isReady()
                        elif c == p.Vmeas and p.Vmade == 0: ## Por si encuentra el valance
                            p.Vmade = 1
                            p.isReady()
                        else: # Buscar de quien es
                            for ii,pp in enumerate(me.ps):
                                if ii==ip:
                                    continue
                                if pp.Lmeas == c:
                                    p.Lqtymade += 1
                                    pp.isReady()
                                elif c == pp.Vmeas and pp.Vmade == 0:
                                    pp.Vmade = 1
                                    p.isReady()
                    mc["veces"] -= 1
                    if p.RDY:
                        break


    def printReport(me, optimizado):
        me.slotterpast = []
        me.slotternow = []
        me.terminados = []
        me.veces = 0

        #print(me.cuts)

        for o in optimizado:
            me.o = o
            #print("Para el corte:", o["cortes"])
            me.veces = 0
            me.slotterpast = []
            for i in range(o["veces"]):
                impreso = False
                me.terminados = []
                me.slotternow = []
                for c in o["cortes"]:
                    me.terminados.append(me.buscarCorte(c))

                if me.slotterpast != []:
                    if me.slotterpast == me.slotternow:
                        me.veces += 1
                    else:
                        if me.veces != 0:
                            me.printForma(o["cortes"], me.veces, me.slotterpast, None)
                        impreso = True
                        me.veces = 1

                    if any(me.terminados) and not impreso:
                        if me.veces != 0:
                            me.printForma(o["cortes"], me.veces, me.slotternow, None)
                        impreso = True
                        me.veces = 0
                else:
                    me.veces += 1

                me.slotterpast = me.slotternow.copy()
            else:
                if not impreso:
                    if me.veces != 0:
                        me.printForma(o["cortes"], me.veces, me.slotternow, None)

    def printForma(me, patron, veces, slots, carro):
        ss =  "Patron:\t" + str(patron) + " --- [//%.2f//] -> %.2f%%\n" % (me.o["scrap"], me.o["Porcentaje"])
        ss += "Slots: \t["
        for i, s in enumerate(slots):
            if me.terminados[i]:
                z = "* "
            else:
                z = " "
            ss += str(s) + z
        ss = ss[:-1] + "]\n"
        ss += "Carro:" + "\n"
        ss += "Veces:  x%d" % veces + "\n\n"

        print(ss)



class persiana:
    def __init__(me, feats, np):
        me.feats = feats
        me.np = np
        me.nps = me.np.split("-")
        me.color = me.nps[1]
        
        me.Lqty = me.feats.loc["LouverQty"] #Cantidad de louvers
        me.Lmeas = me.feats.loc["TrackWidthNumeric"] #Medida de louvers

        me.slot = -1 #Slot
        me.car = -1 #Carro

        me.Lqtymade = 0 #Lo que ya se hizo

        me.RDY = False  #si la persiana esta lista

        
        if me.nps[2] == "40":
            me.LouverLong = 192.
        else:
            me.LouverLong = 82.5

        try:
            me.Vnp = feats.loc["ValanceInsert ComponentNumber"].encode("ascii", errors="ignore").decode().replace(" ","")
            me.Vnps = me.np.split("-")
            me.Vcolor = me.Vnps[1]
            if me.Vnps[2] == "40":
                me.ValanceLong = 192.
            else:
                me.ValanceLong = 82.5
            me.Vbool = me.Vcolor == me.color
            me.Vmeas = me.feats.loc["ValanceBaseWidthNumeric"]
            me.Vmade = 0
        except:
            me.Vnp = None
            me.Vbool = None
            me.Vmade = None
            me.Vmeas = None

    def setCut(me,corte):
        if not me.RDY:
            aff = False
            if me.Lmeas == corte:
                me.Lqtymade += 1
                aff = True
            else:
                if me.Vmade == 0:
                    if me.Vmeas == corte:
                        me.Vmade = 1
                        aff = True

            me.isReady()
            return aff
        else:
            return False


    def isReady(me):
        if not (me.Vmade is None):
            me.RDY = me.Vmade == 1 and me.Lqty == me.Lqtymade
        else:
            me.RDY = me.Lqty == me.Lqtymade
    
    def getVW(me):
        return me.Vmeas



class sortHandler:
    def __init__(me,stockSize,cuts,num_prt,path_r):
        me.num_prt = num_prt
        me.cuts = cuts.sort_values(by=["LouverQty"])
        me.ordhand = ordenes(me.cuts,me.num_prt)

        meas = me.ordhand.computeCuts()

        me.measures = meas[:,0]
        me.counters = meas[:,1]
        me.path_r = path_r
        me.orders = []
        me.ordersSimple = []
        me.ordersForReport = []
        me.stS = stockSize
        me.getOrders()
        #me.printOrders()
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_colwidth', -1)
        print(me.cuts)
        me.ordhand.printReport2(me.ordersSimple)


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

        little = 0.5

        prob.objective = prob.objective == me.stS - little

        prob += me.stS - (c)  >= little , "No menor que cero"
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

            
            me.ordersSimple.append({"cortes" : oor, "veces" : times, "scrap" : scrap, "Porcentaje": perc})
            #me.ordersSimple.append([oor,times,scrap,perc])
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
            num_tot += o["veces"]
       


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

        slot = 1
        carro = 1

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

        sss = ""


        for i,o in enumerate(me.ordersSimple):

            #print(o)

            #print(me.cuts)


            prom_perc += o["scrap"]*o["Porcentaje"] #acumulado de porcentajes de desperdicio
            prom_ft += o["scrap"]*o["veces"] #acumulado de desperdicio en ft
            st += o["scrap"]  #suma total de scrap

        
            ss = "Patron %d:\n" % (i+1)
            ss += "Forma del corte:\n\t"
            ss += str(o["cortes"]) + "\n"
            ss += "x%d ve" % o[1]

            if o["veces"]==1:
                ss += "z\t"
            else:
                ss += "ces\t"
            ss += "\t\tSobrante: %f = %f%%\n" % (o["scrap"], o["Porcentaje"])
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

        me.req.append(me.meanScrapPercent)

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




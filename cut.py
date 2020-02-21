import numpy as np

#global cuts

cuts = np.array([10. , 10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.
                ,10.,10.,10.,10.,10., 10., 10., 10., 10., 10., 10., 10., 10. ,11.
                ,1.,1.,1.,1.,1.,1.,1.,1.,1.,1.])


idx = np.arange(len(cuts))

orders = []

print(idx)
print("#"*10)

Bs = [] #mejores soluciones
st = 100.
Bwaste = st
Bcand = None

def makeOrders(sol,univ):
    sol = np.array(sol)
    solUn, solCnt = np.unique(sol, return_counts=True)
    univUn, univCnt = np.unique(univ, return_counts=True)

    print(solUn)
    print(solCnt)
    print(univUn)
    print(univCnt)

    minn = 10000000
    for i,c in enumerate(solUn): ##Encuentra la mayor cantidad posible de ordenes que se
                    ##pueden hacer con la solucion actual
        n = np.where(univUn == c)[0] ##Encontrar el indice donde esta la 
                                     ##solucion
        m = int(univCnt[n]/solCnt[i])
        if m<minn:
            minn = m
   
    for i in range(minn): # genera las ordenes
        orders.append(sol.copy())
 
    print ("Old")
    print (univ)
    #elimina elementos ya usados en las ordenes
    for i,c in enumerate(solUn):
        idxs = np.where(univ==c)
        until = solCnt[i]*minn
        #print(until)
        idd = np.take(idxs,np.arange(until))
        #print(idd)
        univ = np.delete(univ,idd)

    print("New")
    print(univ)
    idx = np.arange(univ.shape[0])

    return univ

class P:
    def __init__(me,sol,univ,st_size):
        me.univ = univ
        me.st_s = st_size
        me.sol = sol.copy()
        me.deleteme = False
        me.optimal = False

        if sol == []:
            me.s = np.zeros(1)
            me.appr = 0.
        else:
            me.sarr = np.asarray(me.sol)
            me.s = np.array(cuts[me.sarr])
            me.appr = np.sum(cuts[me.sarr])

        me.waste = me.st_s - me.appr

        if me.waste<Bwaste:
            Bcand = me

        if me.waste > 0.1:
            for i in range(me.univ.shape[0]):
                #print("Idx run:", i)
                newsol = me.sol.copy()
                newsol.append(me.univ[i].copy())
                ex = i+1
                try:
                    newuni = me.univ[i+1:]
                except:
                    break
                #input()
                newP = P(newsol,newuni,st)
                if newP.deleteme:
                    del newP
                #if newP.optimal:
                #    makeOrders(newP.s,cuts[newP.univ])

        elif me.waste < 0:
            #me.pinfofail()
            me.deleteme = True
            pass
        else:
            #print("Optimal solution found!!!")
            #me.pinfo()
            #Bs.append(me)
            me.optimal = True
            #input()

    def pinfo(me):
        print("Solution:", me.s)
        print("IDxs:", me.sol)
        print("Waste:",me.waste)

    def pinfofail(me):
        print("Solution:", me.s)
        print("SUM:",me.appr)



Pini = P([],idx,st)
Bcand.pinfo()


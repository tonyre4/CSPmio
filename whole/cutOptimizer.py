import sorter as SS
import pandas as pd
import numpy as np
import sys

def printReq(mat):
    with open("req.txt", "w+") as f:
        f.write("**Requisicion de materiales**\n" + "##"*25 + "\n")
        f.write("Numero de parte\tQty\tTot ft\n")
        for p in mat:
            s = p[0] + "\t" + "%d"%(p[1][0]) + "\t" +  "%.2f"%(p[1][1]) + "\n"
            f.write(s)

        f.write("##" *25)




np.seterr(divide='ignore')

if __name__ == "__main__":

    try:
        csv = sys.argv[1]
    except:
        print("No hay archivo csv de entrada...")
        exit()

    path_r = "./reports/"

    data = pd.read_csv(csv,sep=";")
    
    
    #Solo louvers
    sl = data.dropna(axis=0, subset=['TrackWidthNumeric'])
    
    #color,track_width,qty_cuts
    din = sl.loc[:,["LouverComponentNumber","TrackWidthNumeric","LouverQty"]].copy()
   
    #obtener numeros de parte
    req = [] #lista de requisición
    parts = din.LouverComponentNumber.unique()

    ##para cada numero de parte
    lll = len(parts)
    reqs = []
    for i,pp in enumerate(parts):
   
        p = pp.encode("ascii", errors="ignore").decode().replace(" ","")

        print("Computando solución para numero de parte %s\n%d de %d" % (p,i+1,lll))

        cuts = din.loc[din["LouverComponentNumber"]== pp ,["TrackWidthNumeric","LouverQty"]]
        #Valores de cortes ordenados
        twn = sorted(np.array(cuts.TrackWidthNumeric.unique()))
        
        #Obteniendo el total de cortes por cada medida
        meas = np.empty((0,2))
        for w in twn:
        
            s = cuts.loc[cuts['TrackWidthNumeric']==w].sum()
            meas = np.vstack([meas,[w,s.iloc[1]]])
    
        #Corre optimizador
        A = SS.sortHandler(192.,meas,p,path_r)
        reqs.append([p,A.getReq()])
    
    printReq(reqs)
        #exit()

    

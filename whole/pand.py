import sorter as SS
import pandas as pd
import numpy as np

data = pd.read_csv("vert.csv",sep=";")


#print(data["TrackWidthNumeric"])

#Solo louvers

sl = data.dropna(axis=0, subset=['TrackWidthNumeric'])

#color,track_width,qty_cuts
din = sl.loc[:,["LouverComponentNumber","TrackWidthNumeric","LouverQty"]].copy()

parts = din.LouverComponentNumber.unique()

for p in parts:
    cuts = din.loc[din["LouverComponentNumber"]== parts[0],["TrackWidthNumeric","LouverQty"]]

    twn = sorted(np.array(cuts.TrackWidthNumeric.unique()))

    meas = np.empty((0,2))

    for w in twn:
        s = cuts.loc[cuts['TrackWidthNumeric']==w].sum()
        #print(s.iloc[1])
        
        meas = np.vstack([meas,[w,s.iloc[1]]])



    SS.sortHandler(192.,meas,p)
    exit()

    

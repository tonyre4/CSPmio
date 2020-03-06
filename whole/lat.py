from pylatex import (Document, TikZ, TikZNode,
                     TikZDraw, TikZCoordinate,
                     NoEscape,TikZUserPath, TikZOptions)
import pylatex as pl




def cutReport(num_part,data):
    
    

    space = 0.8

    s = ""

    s+= """\\begin{center}Reporte de cortes\\end{center}\\newline\\newline\bNumero de parte:
        %s\\hline\\hline\\newline""" %(num_part)
    


    for cut in data:
        
        s+= "x %d" % cut[0]

        for c in cut[1]:
            cc = c*space
            s+= """\\begin{tikzpicture}
\\draw (0,0) rectangle (%f\\linewidth,1) node[pos=0.5] {Test};
\\end{tikzpicture}""" % cc

        s+="\\hline\\newline"


    doc = Document()
    doc.append(TikZ())
    doc.append(pl.utils.NoEscape(s))
    doc.generate_pdf('PDFexit', clean_tex=False)

    print (s)

cutReport("6050",[[20,[0.5,0.1,0.1,0.2,0.15,0.15],[0.0,0.0]],[21,[0.1,0.1,0.1],[0.1,17.0]]])

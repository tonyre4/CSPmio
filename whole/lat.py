from pylatex import (Document, TikZ, TikZNode,
                     TikZDraw, TikZCoordinate,
                     NoEscape,TikZUserPath, TikZOptions)
import pylatex as pl




def cutReport(data):
    
    s = ""

    s+= """Reporte de cortes"""

    for c in data:
        s+= """
\\begin{tikzpicture}
\\draw (0,0) rectangle (%f\\linewidth,1) node[pos=0.5] {Test};
\\end{tikzpicture}""" % c


    doc = Document()
    doc.append(TikZ())
    doc.append(pl.utils.NoEscape(s))
    doc.generate_pdf('PDFexit', clean_tex=False)

    print (s)

cutReport([0.5,0.1,0.1,0.2,0.15,0.15,])

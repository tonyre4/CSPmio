from fpdf import FPDF
import pickle


def oneReqMaker(num_prt,lvrs,ft):
    pass

def multiReqMaker(num_prt,lvrs,ft):
    pass

def cutPrinter(pdf,dat,pos):

    pass


def cutReport(num_prt,cuts,path):

    j = (num_prt,cuts,path)

    #with open('var.pickle', 'wb') as f:
    #    pickle.dump(j, f)

    pdf = FPDF(orientation='P', unit='mm', format='letter')
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Cortes", ln=1, align="C")
    pdf.cell(200, 10, txt="Numero de parte: %s"%num_prt, ln=1, align="C")

    pdf.set_fill_color(0, 255, 0)
    pdf.rect(30, 50, 170, 7.5)
    pdf.cell(200, 10, txt="Numero de parte: %s"%num_prt, ln=1, align="C")


    s = "%s/%s_cuts.pdf" % (path.replace(" ",""),num_prt)
    pdf.output(s)


if __name__=="__main__":
    with open('var.pickle','rb') as f:
         j = pickle.load(f)
    num_prt,cuts,path = j
    cutReport(num_prt,cuts,path)

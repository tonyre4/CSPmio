import numpy as np

from scipy.optimize import minimize,brute

global meas

meas = np.array([10.,1.,2.])

def calc(x):
    print("Cortes:")
    print(x)
    print("Por corte:")
    s = x*meas
    print(s)
    print("Suma:")
    su = np.sum(s)
    print(su)
    print("err:")
    e = 100-su
    print(e)
    print(" ")
    if e<0:
        e=1000
    return e

ranges =  (slice(0,9,1),)*3

result = brute(calc,ranges, disp=True, finish= None)

print(result)

calc(result)

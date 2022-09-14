#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 20:13:04 2022

@author: erik
"""
from IPython.display import display, Latex
from functools import wraps
from orderedset import OrderedSet
import sympy
from sympy.core.symbol import symbols, Symbol
from sympy.solvers.solveset import nonlinsolve
from sympy import solveset
from sympy import Eq
from sympy.utilities.lambdify import lambdify
from sympy.printing import latex, pprint
from sympy import Symbol, simplify
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, EngFormatter

from math import log10
from PyLTSpice import LTSpice_RawRead
from sympy.solvers import solve
import sys
import logging
from ipywidgets import FloatSlider, interact, interactive
from converter6 import * #works acceptably with converter3

#logformat = '{asctime}\n{message}'
logformat = '{message}'
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    #handlers somehow stay alive even after restarting iPython
    #console and clearing variables
    logger.handlers.clear()

logger.setLevel('DEBUG')
print(logger)
print(__name__)
# Use FileHandler() to log to a file
file_handler = logging.FileHandler('Problem3-1.log', mode='w')
formatter = logging.Formatter(fmt=logformat, style='{' )
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def make_symbols():
    global R, C, L, D, s, Vc, Vg, VL, iin, iL, iC, iR, fs, M, delta_iL, delta_vC, Ts, Rl
    global eta, Pin, Pout
    
    R = variable('R', 'ohms', None, real=True, positive=True)
    Rl = variable('R_L', 'ohms', None, real=True, positive=True)
    C = variable('C', 'F', None, real=True, positive=True)
    L = variable('L', 'H', real=True, positive=True)
    D = variable('D', '%', real=True, positive=True)
    
    fs = variable('f_s', 'Hz', real=True, positive=True)
    

    Vc = variable('V_c', 'V', real=True)
    Vg = variable('V_g', 'V', real= True)
    VL = variable('V_L', 'V', real= True)

    iin = variable('i_in', 'A', real=True)
    iL = variable('i_L', 'A', real=True)
    iC = variable('i_C', 'A', real=True)
    iR = variable('i_R', 'A', real=True)
    delta_iL = variable('\Delta i_L', 'A', 'delta_iL', real=True)
    delta_vC = variable('\Delta v_C', 'V', 'detla_vC', real=True)
    M = variable('M', real=True)
    eta = variable('eta', real=True)
    Pin = variable('P_in', 'Watts', real=True)
    Pout = variable('P_out', 'Watts', real=True)
    
    return
make_symbols()

buckboost = converter()
buckboost.equations.add( D*(Vg-iL*Rl) + (1-D)*(Vc-iL*Rl) ) #VLavg must equal 0 in steady state#buckboost.equations.add(D*(-Vc/R) + (1-D)*(-Vc/R-iL)) #iCavg must equal 0 in steady state
buckboost.equations.add(M - Vc/Vg)
buckboost.equations.add(eta - Pout/Pin)
buckboost.equations.add(R - Vc/iR)
buckboost.equations.add(Pin - Vg*iin)
buckboost.equations.add(Pout - Vc*iR)
buckboost.showequations()

#myprint(Vc, *buckboost.solver(given={}, want=Vc))
myprint(M, *buckboost.solver(given={}, want=M))
#myprint(eta, *buckboost.solver(given={}, want=eta))
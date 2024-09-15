#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:16:39 2024

@author: erik
"""




import streamlit as st 
import numpy as np 
import sympy
from scipy import constants
import matplotlib.pyplot as plt
import math
from sympy import symbols, pi, sqrt, solve, nonlinsolve, Rational
from sympy.printing import latex
from constraint_helpers import *
from matplotlib.ticker import  EngFormatter


fsw_max = 1e6
fsw_min = 10e3
wsw_max = 2*np.pi*fsw_max
wsw_min = 2*np.pi*fsw_min
Tsw_min = 1/fsw_max
Tsw_max = 1/fsw_min
Lres_min = 1e-10
Lres_max = 1e-3
Cres_min = Lres_min
Cres_max = Lres_max
fres_min = 1/(2*np.pi*np.sqrt(Lres_max*Cres_max))
fres_max = 1/(2*np.pi*np.sqrt(Lres_min*Cres_min))
wres_min = 2*np.pi*fres_min
wres_max = 2*np.pi*fres_max
Lres = variable('L_{res}', 'H', '%.2e', min_value=Lres_min, max_value=Lres_max, step=1e-10, real=True, positive=True)
Cres = variable('C_{res}', 'F', '%.2e', min_value=Cres_min, max_value=Cres_max, step=1e-10, real=True, positive=True)
RL =  variable('R_L', 'Ω', '%.2f', min_value=.001, max_value=1000.0, step=.001, real=True, positive=True)
fres = variable('f_{res}', 'Hz', '%.2e',min_value=fres_min, max_value=fres_max, step=fres_min, real=True, positive=True )
fsw = variable('f_{sw}', 'Hz', '%.2e',min_value=fsw_min, max_value=fsw_max, step=fsw_min, real=True, positive=True)
Tsw = variable('T_{sw}', 's', '%.2e', min_value=Tsw_min, max_value=Tsw_max, step=Tsw_min, real=True, positive=True)
wsw = variable(r'\omega_{sw}', 'rad/s', '%.2e',min_value=wsw_min, max_value=wsw_max, step=wsw_min, real=True, positive=True)
wres = variable(r'\omega_{res}', 'rad/s', '%.2e',min_value=wres_min, max_value=wres_max, step=wres_min, real=True, positive=True)
Vcmax = variable('V_{C,max}', 'V', '%.2f',min_value=10.0, max_value=200.0,step=1.0, real=True, positive=True)
Vin = variable('V_{in}', 'Vin', '%.2f',min_value=10.0, max_value=200.0,step=1.0, real=True, positive=True)
iavg = variable('i_{avg}', 'A', '%.2f',min_value=.1, max_value=20.0,step=.1, real=True, positive=True)
k = variable('k', '', '', min_value=.1, max_value=1.0,step=.1, real=True, positive=True)

varss  = [Lres, Cres, RL, fres, fsw, Tsw, wsw, wres, Vcmax, Vin, iavg, k]

eq1 = Cres - iavg/(2*fres*Vcmax)
eq2 = fres - 1/(2*pi*sqrt(Lres*Cres))
eq3 = wres - 2*pi*fres
eq4 = Tsw - 1/fsw
eq5 = fres - k*fsw
eqs = [eq1, eq2, eq3, eq4, eq5]

for var in varss: 
    if str(var) not in st.session_state:
        st.session_state[str(var)] = 0

if 'sym_sols' not in st.session_state:
    st.session_state.sym_sols = {str(var): None for var in varss}

def cau(*args):
    
    '''
    Parameters
    ----------
    *args : TYPE
        DESCRIPTION.

    Returns
    -------
    since nonlinsolve has no tolerance on accepting old solutions, 
    try a numeric solve when the nonlinsolve comes up empty. 
    Initial guesses are what is known already. 
    '''
    
    var = args[0]
    def zipsys(varss, inputs):
        '''
        Parameters
        ----------
        varss : list of symbols in the system
        inputs : {var, value} where value is a float or None

        Returns
        -------
        To increase the chance of solver being able to use prior solutions, 
        use symbolic result from sym_sols if one is there. 

        But, don't replace the index sym for which the callback was called
        since that has changed from user. 
        
        There may be numbers in number_inputs already, and the symbolic form
        is already in sym_sols. 
        '''
        given = []
        #print(f'symsols: {st.session_state.sym_sols}')
        #print(var)
        for s, v in inputs.items():
            #print(f'str s: {s}')
            #print(f'v: {v}')
            if str(s) != var: #not appending the var for which callback was called 
                try:
                    print(f'appending var {s} = {st.session_state.sym_sols[str(s)]} ')
                    #already rational: 
                    given.append(s - st.session_state.sym_sols[str(s)])  
                except TypeError:
                    pass

            else: #don't think this should ever fail with TypeError because
            #this catches the new one 
                try:
                    given.append(s - Rational(v))
                except TypeError:
                    print('caught type error!')
                    #print(s)
                    #print(v)
                    pass                 
        return given
    
    def my_remove(var, inputs):
        '''
        
        Parameters
        ----------
        var: string from  compute_and_update (cau) callback arg
        inputs: {var: value}, where value is from number_inputs 
        Returns
        -------
        inputs with a value removed that isn't var. 
        
        It would be nice to remove the var that would leave the most solutions
        . 
        You could try more than one, and stick with the one that leaves 
        the most answers. Or, use the eqs, pick one from an equation 

        '''
   
        for s in inputs.keys():
            if inputs[s] != None and str(s) != var:
                print(f'removing {s} = {inputs[s]}')
                inputs[s] = None
                st.session_state.sym_sols[str(s)] = None 
                break
        return inputs
    

    inputs = {var: st.session_state[str(var)] for var in varss} #from number_inputs
    print(f'inputs: {inputs}')
    #the total system is the constraints plus what is input 
    mysys = eqs + zipsys(varss, inputs)  
    print(mysys)
    ans = filter_solutions(nonlinsolve(mysys, varss ), varss) 
    print(f'filtered before loop: {ans} \n')
    if len(ans)==0:
        for j in range(len(varss)): #only try len(varss) times 
            
            print('caught empty set')
            #remove an input that is not the newest and also isn't already None
            inputs = my_remove(var, inputs)
            mysys = eqs+ zipsys(varss, inputs)  
            print(mysys)
            ans = filter_solutions(nonlinsolve(mysys, varss ),varss) 
            if len(ans) > 0:
                break 

    print(f'filtered: {ans} \n')
    
    for sol in ans: #what if there is no sol?  
        
        for var, res, i in zip(varss, sol, range(len(varss))):
            #if there are no symbols in the expression, save it 
            with results[ i % (num_cols - 1)]:
            
                if len(res.free_symbols) == 0:
                    #we're in a callback that won't be called until a number_input 
                    #changes. results is an already created container in an st.empty
                    #object. 
                    st.session_state.sym_sols[str(var)] = res #keep it rational 
                    st.session_state[str(var)] = float(res)
                    st.latex(latex(var) +' = '  + process_res(var, res ))
                    
                else: 
                    st.latex(latex(var) +' = '  + latex(res.evalf(4)))
                    st.session_state[str(var)] = None 
                
    return 


num_cols = 4
cols = st.columns(num_cols)
num_fields = len(varss)

#split up all the var number_inputs amongst the columns 
for i, var in zip(range(len(varss)), varss):
    col = i % num_cols
    with cols[col]:
        st.number_input(label = '$'+str(var)+ r'\,\, [\text{'+ var.unit + r'}]$',
                        value=None,
                        min_value=var.min,
                        max_value=var.max,
                        step=var.step,
                        format=var.format if var.format !='' else None,
                        key=str(var),
                        on_change=cau,
                        args=(str(var),))
num_cols = 3
cols = st.columns(num_cols)
results = {}

#want to create two columns and put an empty container in each 
for col, i in zip(cols[:-1], range(len(cols) - 1)):
    #one column reserved to display constraints 
    results[i] = col.empty().container()
 
with cols[-1]:
    for eq in eqs:
        st.latex(myprint2(eq))
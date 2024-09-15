#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 11:39:00 2024

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

Lres, Cres, RL = symbols('L_{res} C_{res}, R_L', real=True, positive=True)
fres, fsw, Tsw, wsw, wres = symbols(r'f_{res} f_{sw}, T_{sw}, \omega_{sw}, \omega_{res}', real=True, positive=True)
Vcmax, Vin, iavg, k = symbols('V_{Cmax}, V_{in}, i_{avg}, k', real=True, positive=True)
eq1 = Cres - iavg/(2*fres*Vcmax)
eq2 = fres - 1/(2*pi*sqrt(Lres*Cres))
eq3 = wres - 2*pi*fres
eq4 = Tsw - 1/fsw
eq5 = fres - k*fsw
eqs = [eq1, eq2, eq3, eq4, eq5]


syms = [Lres, Cres, RL, fres, fsw, Tsw, wsw, wres, Vcmax, Vin, iavg, k]


for sym in syms: 
    if str(sym) not in st.session_state:
        st.session_state[str(sym)] = 0

if 'sym_sols' not in st.session_state:
    st.session_state.sym_sols = {str(sym): None for sym in syms}


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
    
    sym = args[0]
    def zipsys(syms, inputs):
        '''
        Parameters
        ----------
        syms : list of symbols in the system
        inputs : {sym, value} where value is a float or None

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
        print(f'symsols: {st.session_state.sym_sols}')

        for s, v in inputs.items():
            if str(s) != sym:
                try:
                    print(f'appending sym {s} = {st.session_state.sym_sols[str(s)]} ')
                    #already rational: 
                    given.append(s - st.session_state.sym_sols[str(s)])  
                except TypeError:
                    pass

            else: #don't think this should ever fail with TypeError becuase
            #this catches the new one 
                try:
                    given.append(s - Rational(v))
                except TypeError:
                    pass                 
        return given
    
    def my_remove(sym, inputs):
        '''
        
        Parameters
        ----------
        sym: string from  compute_and_update (cau) callback arg
        inputs: {sym: value}, where value is from number_inputs 
        Returns
        -------
        inputs with a value removed that isn't sym. 
        
        It would be nice to remove the sym that would leave the most solutions
        . 
        You could try more than one, and stick with the one that leaves 
        the most answers. Or, use the eqs, pick one from an equation 

        '''
   
        for s in inputs.keys():
            if inputs[s] != None and str(s) != sym:
                print(f'removing {s} = {inputs[s]}')
                inputs[s] = None
                st.session_state.sym_sols[str(s)] = None 
                break
        return inputs
    

    inputs = {sym: st.session_state[str(sym)] for sym in syms} #from number_inputs
    #the total system is the constraints plus what is input 
    mysys = eqs + zipsys(syms, inputs)  
    print(mysys)
    ans = filter_solutions(nonlinsolve(mysys, syms ), syms) 
    print(f'filtered before loop: {ans} \n')
    if len(ans)==0:
        for j in range(len(syms)): #only try len(syms) times 
            
            print('caught empty set')
            #remove an input that is not the newest and also isn't already None
            inputs = my_remove(sym, inputs)
            mysys = eqs+ zipsys(syms, inputs)  
            print(mysys)
            ans = filter_solutions(nonlinsolve(mysys, syms ),syms) 
            if len(ans) > 0:
                break 

    print(f'filtered: {ans} \n')
    
    for sol in ans: #what if there is no sol?  
        
        for sym, res in zip(syms, sol):
            #if there are no symbols in the expression, save it 
            if len(res.free_symbols) == 0:
                #we're in a callback that won't be called until a number_input 
                #changes. results is an already created container in an st.empty
                #object. 
                results.latex(latex(sym) +' = '  + latex(res.evalf(4)))
                st.session_state.sym_sols[str(sym)] = res #keep it rational 
                st.session_state[str(sym)] = float(res)
            else: 
                results.latex(latex(sym) +' = '  + latex(res.evalf(4)))
                st.session_state[str(sym)] = None 
                
    return 


num_cols = 3
cols = st.columns(num_cols)
num_fields = len(syms)

#split up all the symbol number_inputs amongst the columns 
for i, s in zip(range(len(syms)), syms):
    col = i % num_cols
    with cols[col]:
        st.number_input(label = '$'+str(s)+'$', value=None,format='%.2f',key=str(s), on_change=cau, args=(str(s),))

        

       
col3, col4 = st.columns(2)    
with col3: 
    results = st.empty().container()
with col4:
    for eq in eqs:
        st.latex(myprint2(eq))
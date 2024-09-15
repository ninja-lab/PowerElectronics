#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 18:41:43 2024

@author: erik

issues: 
    1. starting with only inputing, a: TypeError: cannot determine truth value of Relational from nonlinsolve,
    but solve works. 
    2. rounding error when taking an old solution, it no longer perfectly satisfies a new solution 
    3. any ideas for a numerical solution? 
    4. the problem with solve is eqs = [a - b*c, c - d - e, e - f**2, e - 16.0, f - 4.0] throws
    Not Implemented Error, but nonlinsolve works 
    5. order of printing solutions from callback - how to get them below the inputs? 
"""



import streamlit as st 
import numpy as np 
import sympy
from scipy import constants
from scipy.integrate import dblquad
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, EngFormatter
import math
from sympy import symbols, pi, sqrt, solve, nonlinsolve
from sympy.printing import latex
eps_0 = constants.epsilon_0

a,b,c = symbols('a b c', real=True, positive=True)
d, e, f = symbols('d e f', real=True, positive=True)
syms = [a,b,c,d,e,f]
eq1 = a - b*c
eq2 = c - (d + e)
eq3 = e - f**2
eqs = [eq1, eq2, eq3,]

if 'a' not in st.session_state:
    st.session_state.a = 0 
if 'b' not in st.session_state:
    st.session_state.b = 0 
if 'c' not in st.session_state:
    st.session_state.c = 0 
if 'd' not in st.session_state:
    st.session_state.d = 0 
if 'e' not in st.session_state:
    st.session_state.e = 0 
if 'f' not in st.session_state:
    st.session_state.f = 0 
if 'sym_sols' not in st.session_state:
    st.session_state.sym_sols = {str(sym): None for sym in syms}
##print('at beginning:\n')
#print(st.session_state.sym_sols)
#st.write("Initial session state:")
#st.write(st.session_state)
#print(f'syms: {syms}')


def myprint(*args):
    '''  
    the first argument is the only "lhs"
    subsequent arguments are rhs-s
    '''
    
    def helper(args):
        if len(args) == 0:
            return ''
        else: 
            return f'= {latex(args[0])}' + helper(args[1:])
        
    s = f'{latex(args[0])} {helper(args[1:])}' 
    return s 
    
def myprint2(eq):
    #if isinstance(eq2.func, sympy.core.add.Add):
    if eq.func == sympy.core.add.Add:
        lhs = eq.args[0]
        rhs = eq - lhs
        #print('hello')
        #st.latex( myprint(-1*lhs, rhs))
        return myprint(lhs, -1*rhs)

    else:
        return type(eq)
        print('didnt work')
        
    return
def filter_solutions(solutions, symbols):
    def satisfies_assumptions(solution, symbols):
        for sol, symbol in zip(solution, symbols):
            # Check assumptions only for numeric elements
            if sol.is_number:
                assumptions = symbol.assumptions0
                if assumptions.get('positive', False) and not sol.is_positive:
                    return False
                if assumptions.get('negative', False) and not sol.is_negative:
                    return False
                if assumptions.get('real', False) and not sol.is_real:
                    return False
        return True

    return {sol for sol in solutions if satisfies_assumptions(sol, symbols)}

def cau(*args):
    i = args[0]
    def zipsys(syms, inputs):
        given = []
        print(f'symsols: {st.session_state.sym_sols}')
    #grab inputs from number_inputs, but replace with sym representation 
    #if they are there, since those will be from a prior solution. 
    #But, don't replace the index i since that has changed from user. 
        for s, v in zip(syms, inputs):
            
            try: 
                given.append(s - st.session_state.sym_sols[str(s)])
            except TypeError:
                try:
                    given.append(s - v)
                except TypeError:
                    pass 
        return given
    
    def my_remove(i, inputs):
        '''
        
        Parameters
        ----------
        i : index of newest variable not to remove
        inputs : [float, none, none, float, i, float]

        Returns
        -------
        None.

        '''
        for k in range(len(inputs)):
            if inputs[k] != None and k !=i:
                print(f'removing {k} = {inputs[k]}')
                inputs[k] = None
                break
        return inputs
    

    inputs = [st.session_state.a, 
              st.session_state.b,
              st.session_state.c,
              st.session_state.d,
              st.session_state.e,
              st.session_state.f]
 
    
    mysys = eqs + zipsys(syms, inputs)  
    print(mysys)
    ans = filter_solutions(nonlinsolve(mysys, syms ), syms) 
    print(f'filtered before loop: {ans} \n')
    if len(ans)==0:
        for j in range(len(syms)): #only try len(syms) times 
            
            print('caught empty set')
            #remove an input that is not the newest and also isn't already None
            inputs = my_remove(i, inputs)
            #inputs[i] = None
            mysys = eqs+ zipsys(syms, inputs)  
            print(mysys)
            ans = filter_solutions(nonlinsolve(mysys, syms ),syms) 
            if len(ans) > 0:
                break 
    #fil = filter_solutions(ans, syms)
    print(f'filtered: {ans} \n')
    
    for sol in ans: #what if there is no sol? there must have been solutions 
    #otherwise the while loop would never exit 
        
        for sym, res in zip(syms, sol):
            #if isinstance(res, float):
            #    st.write(latex(sym) + ' = '+ f'{res:.2e}')
            #print(type(res))
            results.latex(latex(sym) +' = '  + latex(res))
            if isinstance(res, sympy.core.numbers.Float):
                #also save symbolic representation to be used in next round 
                st.session_state.sym_sols[str(sym)] = res
                st.session_state[str(sym)] = float(res)
            else: 
                st.session_state[str(sym)] = None 
                
    return 
col1, col2, col3 = st.columns(3)
with col1:
    
    st.number_input(label = '$a$',  value=None,format='%.2f',key='a', on_change=cau, args=(0,))
    #st.button(label='clr Vcmax')
    st.number_input(label = r'$b $', format='%.2f', value=None, key='b', on_change=cau, args = (1,))
with col2:
    st.number_input(label = r'$c$', format='%.2f' ,value=None, key='c', on_change=cau, args = (2,))  
    st.number_input(label = '$d$', value=None,format='%.2f',key='d', on_change=cau, args=(3,))
with col3:
    st.number_input(label = r'$e $', format='%.2f', key='e', value=None, on_change=cau, args=(4,))
    st.number_input(label = r'$f $', format='%.2f', key='f', value=None, on_change=cau, args=(5,))


       
col3, col4 = st.columns(2)    
with col3: 
    results = st.empty().container()
with col4:
    for eq in eqs:
        st.latex(myprint2(eq))


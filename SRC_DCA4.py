#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:05:33 2024

@author: erik
"""




import streamlit as st 
import numpy as np 
import sympy
from scipy import constants
from scipy.integrate import dblquad
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, EngFormatter
import math
from sympy import symbols, pi, sqrt, solve, nonlinsolve, Rational
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
        '''
        given = []
        print(f'symsols: {st.session_state.sym_sols}')

        for s, v in inputs.items():
            if str(s) != sym:
                try:
                    print(f'appending sym {s} = {st.session_state.sym_sols[str(s)]} ')
                    given.append(s - st.session_state.sym_sols[str(s)])  
                except TypeError:
                    print(f'type error on sym {s}')
            
                    try: #can there ever be a prior number_input when there is no sym_sol?  
                        print(f'appending float {s} = {v} ')
                        given.append(s - v)
                    except TypeError:
                        pass 
            else: #don't think this should ever fail with TypeError 
                try:
                    given.append(s - v)
                except TypeError:
                    pass                 
        return given
    
    def my_remove(sym, inputs):
        '''
        
        Parameters
        ----------
        sym: string from  compute_and_update (cau) callback
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

            results.latex(latex(sym) +' = '  + latex(res))
            if isinstance(res, sympy.core.numbers.Float):
                #also save symbolic representation to be used in next round 
                #better yet, save as rational approximation 
                st.session_state.sym_sols[str(sym)] = Rational(res.evalf(5))
                st.session_state[str(sym)] = float(res)
            elif isinstance(res, sympy.core.numbers.Integer):
                st.session_state.sym_sols[str(sym)] = res
            else: 
                st.session_state[str(sym)] = None 
                
    return 
col1, col2, col3 = st.columns(3)
with col1:
    st.number_input(label = '$a$',  value=None,format='%.2f',key='a', on_change=cau, args=('a',))
    st.number_input(label = r'$b $', format='%.2f', value=None, key='b', on_change=cau, args = ('b',))
with col2:
    st.number_input(label = r'$c$', format='%.2f' ,value=None, key='c', on_change=cau, args = ('c',))  
    st.number_input(label = '$d$', value=None,format='%.2f',key='d', on_change=cau, args=('d',))
with col3:
    st.number_input(label = r'$e $', format='%.2f', key='e', value=None, on_change=cau, args=('e',))
    st.number_input(label = r'$f $', format='%.2f', key='f', value=None, on_change=cau, args=('f',))


       
col3, col4 = st.columns(2)    
with col3: 
    results = st.empty().container()
with col4:
    for eq in eqs:
        st.latex(myprint2(eq))


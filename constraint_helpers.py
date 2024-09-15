#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 13:58:11 2024

@author: erik
"""


from sympy.printing import latex
from sympy.core.symbol import Symbol
import sympy 
from matplotlib.ticker import  EngFormatter
import math 
from statistics import median
import numpy as np 

class variable(sympy.core.symbol.Symbol):
    #def __new__(self, name, *args, min_value = None, max_value=None, step=None, **assumptions):
        #obj = Symbol.__new__(self, name, **assumptions )
    def __new__(cls, name, *args, min_value=None, max_value=None, step=None, **assumptions):
        obj = Symbol.__new__(cls, name, **assumptions)
        obj.format = args[1] if len(args)>1 else None
        obj.unit = args[0] if len(args)>0 else ''
        obj.min = min_value
        obj.max = max_value
        obj.step = step
        obj.guess = median(np.logspace(np.log10(obj.min), np.log10(obj.max)))
        obj.value = None 
        return obj
    
    '''
    def __str__(self):
        if self.unit is not None: 
            return super().__str__() + f' {self.unit}'
        else: 
            return super().__str__()
    '''
    
    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.guess if self.value is None else self.value
        
    def show_self(self):
        #try:
        return latex(self) + f' = {self.value:{self.format}} {self.unit}'
        #except ValueError:
            
     
        

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
        return myprint(-1*lhs, rhs)

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


def count_sig_figs(digits):
    '''Return the number of significant figures of the input digit string'''

    integral, _, fractional = digits.partition(".")

    if fractional:
        return len((integral + fractional).lstrip('0'))
    else:
        return len(integral.strip('0'))

def power_of_10(num):
    # Get the power of 10
    power = int(math.log10(abs(num)))
    # Adjust the number accordingly
    adjusted_num = num / (10 ** power)
    return adjusted_num, power

def disp_ans(ans, greek_letter, unit):
   try:
       ans1, ans2 = power_of_10(ans)
   except ValueError as e:
       return '= NaN'    
   if ans2 == 0:
       return f'= {ans1:.2f}'  + r'\,'+ greek_letter+  r'\text{' + unit + '}'
   if ans2 == 1:
       return f'= {ans1*10:.2f}'  + r'\,'+ greek_letter+  r'\text{' + unit + '}'
   if ans2 == -1:
       return f'= {ans1/10:.2f}'   + r'\,'+ greek_letter+  r'\text{' + unit + '}'
   #if ans2 is not 
   #    return f'= {ans1*100:.1f}'  + r'\,'+ greek_letter+  r'\text{' + unit + '}'
   else: 
       return f'= {ans1/10:.2f}' +  r'\cdot'+ \
       r'10^{'+ f'{ans2+1}' + r'}\,' + greek_letter+  r'\text{' + unit + '}'

def process_res(var, res):
    '''
    

    Parameters
    ----------
    var : variable instance, subclass of sympy Symbol 
    res : result expression from nonlinsolve known to not have free symbols

    Returns
    -------
    A latex string with a number, a (possiblebly greek) letter representing a power of 10
    that is a multiple of 3 (Giga, Mega, kilo, milli, micro, nano) and a unit 
    
    >>>process_res(Lres, 0.000120)
    120 uH

    >>>process_res(fsw, 1234.56)
    1.23 kHz
    '''
    formatter = EngFormatter(places=3)
    
    #n, e = power_of_10(res.evalf())

   
    #return  formatter.format_eng(round(float(res.evalf()),3)) + var.unit
    expr = formatter.format_eng(res.evalf())
    letter = expr[-1]
    num = expr[:-1]
    
    return  num + r'\,\, \text{'+ letter + var.unit + r'}'

'''
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
    
        st.number_input(label = '$V_{C,max}$',  min_value=5, max_value=100, value=None,
                        step=5,format='%d',key='Vcmax_inp', on_change=newVcmax)
        #st.button(label='clr Vcmax')
        st.number_input(label = r'$L_{res} = $', format='%f', value=None, key='Lres_inp')
        st.number_input(label = r'$C_{res} = $', format='%f', value=None, key='Cres_inp')  
    
    with col2:
        st.number_input(label = '$i_{avg}$',  min_value=1, max_value=20, value=None, step=5,format='%d',key='iavg_inp')
        st.number_input(label = r'$f_{sw} = 1/T_{sw} = $', format='%f', key='fsw_inp', value=None)

    with col3: 
        #st.number_input(label = 'n',  min_value=0, max_value=10, value=1, step=1,format='%d',key='n')
        st.number_input(label = r'$k = \frac{f_{res}}{f_{sw}} = $', format='%f',
                        min_value=.1, max_value=10.0, value=None, step=.1 , key='k_inp')  
    with col4: 
        #st.number_input(label = r'$V_{in}$',min_value=5, max_value=100, value=20, step=5,format='%d', key='Vin')
        st.number_input(label = r'$R_L$',min_value=.1, max_value=100.0, value=None, key='RL_inp')
        st.number_input(label = r'$T_{sw} = 1/f_{sw} = $', format='%f', key='Tsw_inp', value=None)
        st.number_input(label = r'$f_{res} = k\cdot f_{sw}= $', format='%e', key='fres_inp', value=None)
'''
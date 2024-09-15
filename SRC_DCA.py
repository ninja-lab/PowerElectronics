#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 14:29:10 2024

@author: erik
"""

import streamlit as st 
import numpy as np 
from scipy import constants
from scipy.integrate import dblquad
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, EngFormatter
import math
from sympy import symbols, pi, sqrt, solve
eps_0 = constants.epsilon_0
#pi = np.pi
#sqrt = np.sqrt
#log = np.log 
#exp = np.exp
formatter = EngFormatter()

Lres, Cres, RL = symbols('L_res C_res, RL', real=True, positive=True)
fres, fsw, Tsw, wsw, wres = symbols(r'f_res f_sw, T_sw, \omega_sw, \omega_res', real=True, positive=True)
Vcmax, Vin, iavg, k = symbols('V_cmax, V_in, i_avg, k', real=True, positive=True)
eq1 = Cres - iavg/(2*fres*Vcmax)
eq2 = fres - 1/(2*pi*sqrt(Lres*Cres))
eq3 = wres - 2*pi*fres
eq4 = Tsw - 1/fsw
eq5 = fres - k*fsw


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
    return adjusted_num*10, power-1

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
def tester(ans, greek_letter, unit):
    return f'= {ans:.2f}'  + r'\,'+ greek_letter+r'\text{' + unit + '}'
def tester2(ans, greek_letter, unit):
    print( f'= {ans:.2f}'  + r'\,'+ greek_letter+'\text{' + unit + '}')

col1, col2, col3, col4 = st.columns(4)
with col1: 

    st.number_input(label = '$V_{C,max}$',  min_value=5, max_value=100, value=50,
                    step=5,format='%d',key='Vcmax_inp')
    st.number_input(label = r'$L_{res} = $', format='%e', key='Lres_input')
    st.number_input(label = r'$C_{res} = $', format='%e', key='Cres_input')  

with col2:
    st.number_input(label = '$i_{avg}$',  min_value=1, max_value=20, value=10, step=5,format='%d',key='iavg_inp')
    st.number_input(label = r'$f_{sw} = $', format='%e', key='fsw_input')
    st.number_input(label = r'$f_{res} = $', format='%e', key='fres_input')
with col3: 
    st.number_input(label = 'n',  min_value=0, max_value=10, value=1, step=1,format='%d',key='n')
    st.number_input(label = r'$k = \frac{f_{res}}{f_{sw}} = $', format='%f',
                    min_value=.1, max_value=10.0, value=.5, step=.1 , key='k_inp')  
with col4: 
    st.number_input(label = r'$V_{in}$',min_value=5, max_value=100, value=20, step=5,format='%d', key='Vin')
    st.number_input(label = r'$R_L$',min_value=.1, max_value=100.0, value=1.0, key='RL')

#ans = f'{st.session_state.Lres_input}'
#st.latex(r' L_{res} ' + disp_ans(st.session_state.Lres_input, r'', 'H') \
#         + disp_ans(st.session_state.Lres_input*1e6, r'\mu', 'H') \
#             + disp_ans(st.session_state.Lres_input*1e9, r'\text{n}', 'H'))

#if 'f_res' not in st.session_state:
#st.session_state['f_res'] = st.session_state.k*st.session_state.fsw_input
#Cres = formatter.format_eng(st.session_state.Cres_input)
#if 'Cres' not in st.session_state:
#st.session_state['Cres'] = \
#    st.session_state.Iout/(2*st.session_state.f_res*st.session_state.Vcmax)

w_res = 2*pi*st.session_state.f_res
C_res_str = r' C_{res} = \frac{i_{avg}}{2f_{res}V_{C,max}}' + f'={st.session_state.Cres}' +r'\text{F}'
f_res_str = r'f_{res} = 1/(2\pi\sqrt{L_{res}C_{res}})\, ' + f'={st.session_state.f_res:.2e}'
#st.write(C_res_str +r',\quad ' + f_res_str)
st.latex(C_res_str +r',\quad ' + f_res_str) 
wsw = formatter.format_eng(st.session_state.fsw_input*2*pi)
fsw = formatter.format_eng(st.session_state.fsw_input)
st.latex(r'\omega_{sw} = 2\pi f_{sw} = 2\pi\cdot'+f'{fsw}'+r'\text{Hz}'+ f'={wsw}' +r'\text{rad/s}') 
Ts = formatter.format_eng(1/st.session_state.fsw_input)
st.latex('T_{sw} = 1/f_{sw} = '+f'{Ts}s')
st.latex(r'Q_{L} = \omega L/R_L')
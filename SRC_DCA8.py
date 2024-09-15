#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:35:19 2024

@author: erik
"""

import streamlit as st 
import numpy as np 
import sympy
from scipy import constants
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import math
from sympy import symbols, pi, sqrt, solve, nonlinsolve, Rational, nsolve
from sympy.printing import latex
from constraint_helpers import *
from matplotlib.ticker import  EngFormatter
from statistics import median 
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
Rl_min=.1
Rl_max=1000.0
Q_min = wres_min*Lres_min/Rl_max
Q_max = wres_max*Lres_max/Rl_min

Lres = variable('L_{res}', 'H', '%.2e', min_value=Lres_min, max_value=Lres_max, step=1e-10, real=True, positive=True)
Cres = variable('C_{res}', 'F', '%.2e', min_value=Cres_min, max_value=Cres_max, step=1e-10, real=True, positive=True)
RL =  variable('R_L', 'Ω', '%.2f', min_value=Rl_min, max_value=Rl_max, step=.01, real=True, positive=True)
fres = variable('f_{res}', 'Hz', '%.2e',min_value=fres_min, max_value=fres_max, step=fres_min, real=True, positive=True )
fsw = variable('f_{sw}', 'Hz', '%.2e',min_value=fsw_min, max_value=fsw_max, step=fsw_min, real=True, positive=True)
Tsw = variable('T_{sw}', 's', '%.2e', min_value=Tsw_min, max_value=Tsw_max, step=Tsw_min, real=True, positive=True)
wsw = variable(r'\omega_{sw}', 'rad/s', '%.2e',min_value=wsw_min, max_value=wsw_max, step=wsw_min, real=True, positive=True)
wres = variable(r'\omega_{res}', 'rad/s', '%.2e',min_value=wres_min, max_value=wres_max, step=wres_min, real=True, positive=True)
Vcmax = variable('V_{C,max}', 'V', '%.2f',min_value=10.0, max_value=200.0,step=1.0, real=True, positive=True)
Vin = variable('V_{in}', 'Vin', '%.2f',min_value=10.0, max_value=200.0,step=1.0, real=True, positive=True)
iavg = variable('i_{avg}', 'A', '%.2f',min_value=.1, max_value=20.0,step=.1, real=True, positive=True)
k = variable('k', '\,', '%.3f', min_value=.01, max_value=1.0,step=.01, real=True, positive=True)
Q = variable('Q', '\,', '', min_value=Q_min, max_value=Q_max, step=(Q_max-Q_min)/100, real=True, positive=True)

varss  = [Lres, Cres,  fres, fsw, Tsw, wres, Vcmax,  iavg, k, Q, RL]



eq1 = Cres - iavg/(2*fres*Vcmax)
eq2 = fres - 1/(2*pi*sqrt(Lres*Cres))
eq3 = wres - 2*pi*fres
eq4 = Tsw - 1/fsw
eq5 = fres*k - fsw
eq6 = Q - wres*Lres/RL
eqs = [eq1, eq2, eq3, eq4, eq5, eq6]

class UCException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message




def func2(x):
    '''
    
    Parameters
    ----------
    x : array of values of len(varss)

    Returns
    -------
    the equations evaluated with all the values

    To do: put the array of values as the values in a dictionary so that 
    subs can be used. Also need len(varss) worth of equations. 
    there are certain number of equations e
    there are some number of unknowns u, known k: u + k = v
    The known are in sym_sols and can added as equations. 
    
    '''
    d = {str(k):v for k,v in zip(varss, x)}
    
    given = []
    
    #u = sum(1 for v in st.session_state.sym_sols.values() if v is None)
    #k = len(varss) - u
    
    
    for s, v in st.session_state.sym_sols.items():
        try:
            #this needs to be a subtraction from appropriate 
            #element in x, which is d[s] 
            given.append(d[s] - st.session_state.sym_sols[str(s)].evalf())  
        except TypeError:
            pass
        except AttributeError:
            pass
    filt_d = {k: v for k, v in st.session_state.sym_sols.items() if v is None}
    #for s,v in filt_d.items():
    #if len(eqs + given ) < len(varss):
    #    raise UCException("len(eqs + given ) < len(varss)")
        #need to add equations from guesses 
        #this will affect how good the solution is / how close the roots are to 0
        #filt_d has the None's for which we can insert guesses 
        #d[s] is the value that came in x 
        #given.append(d[s] - d[k].guess)
    return [eq.subs(d) for eq in eqs] + given


#sol = fsolve(func, [v.get_value() for v in varss])




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
    #would it be better to substitute in what is known instead of adding 
    #equations? 
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
    print(f'num ans: {len(ans)}')
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
                    var.set_value = float(res)
                    st.latex(latex(var) +' = '  + process_res(var, res ))
                    
                else: 
                    st.latex(latex(var) +' = '  + latex(res.evalf(4)))
                    st.session_state[str(var)] = None 
        break #cludgy way to not display multiple results for now 
                
    return 

def fsolve_button():
    try:
        root = fsolve(func, [var.get_value() for var in varss])
        print(root)
    except UCException as e:
        print('fsolve doesn"t work')
    except TypeError:
        print("fsolve and custom exception didn't work")
        
def fsolve_button2():

    def func(x, eqs, varss):
        d = {k:v for k,v in zip(varss, x)} 
        
        return [eq.subs(d).evalf() for eq in eqs]
        
    given = []    
    varss_d = {str(v): v for v in varss}
    for s, v in st.session_state.sym_sols.items():
        if(len(given+eqs) >= len(varss)):
            print('breaking')
            break
        try:
            #this needs to be a subtraction from appropriate 
            #symbol so the subs works the same 
            #s is a str representing symbol 
            print('appending')
            given.append(varss_d[s] - v.evalf())  
        except TypeError as e:
            raise e
        except AttributeError as e:
            pass #raise e 

   # inputs = {
   #     k: (float(v.evalf()) if v is not None else varss_d[k].guess)
   #     for k, v in st.session_state.sym_sols.items()
   # }

    inputs_known = {
        k: float(v.evalf()) 
        for k, v in st.session_state.sym_sols.items()
        if v is not None
    }

    inputs_unknown = {
        k: varss_d[k].guess
        for k, v in st.session_state.sym_sols.items()
        if v is None
    }

    inputs  = {**inputs_known, **inputs_unknown}
    eqs.extend(given)
    for s, v in inputs_unknown.items():
        if(len(eqs) >= len(varss)):
            print('breaking')
            break
        eqs.extend([varss_d[s] - k])
        
    try:
        
        root = fsolve(func, list(inputs.values()) , args=(eqs, varss))
        print(root)
    except UCException as e:
        print('fsolve doesn"t work')
    except TypeError as e:
        print("fsolve and custom exception didn't work")
        print(len(list(inputs.values())))
        print(len(eqs+given))
        print(given)
        raise(e)

def nsolve_button():
    '''
    

    Returns
    -------
    the initial guess is what is known plus median values of domains 
    Two ways: 
        1. The system is the constraints with known values subbed in. Then, only find 
        roots that determine the remaining variables. 
        
        2. the system is the constraints plus added equations for what is known - 
         this will ensure the known values don't change since they must be satisfied
    '''
    def make_subs(eqs, vals):
        return [eq.subs(vals) for eq in eqs ]
    inputs = {var: st.session_state[str(var)] for var in varss}
    
    guesses = {}
    known = {}
    for k, v in inputs.items():
        if v != None:
            known[k] = v
            #choose something in the domain of k 
            #might want to check if the domain spans more than one order of magnitude 
        else:
            guesses[k] = median(np.logspace(np.log10(k.min), np.log10(k.max)))
    subbed = make_subs(eqs, known) #don't want to sub in the median of domain 
    print('subbed:')
    print(subbed)
    #remove keys and values that were known already 
    #but 
    print(f'# unknown: {len(list(guesses.keys()))}')
    print(f'# eqs: {len(subbed)}')
    ans = nsolve(subbed, list(guesses.keys()), list(guesses.values()))
    print(ans)

def clear_button(): 
    for var in varss: 
        st.session_state[str(var)] = None
        st.session_state.sym_sols = {str(var): None for var in varss}
        
st.button('fsolve', on_click=fsolve_button2)        
#st.button('nsolve', on_click=nsolve_button)
st.button('clear', on_click=clear_button)
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
with st.container():
    #want to create two columns and put an empty container in each 
    for col, i in zip(cols[:-1], range(len(cols) - 1)):
        #one column reserved to display constraints 
        results[i] = col.empty().container()
     
    with cols[-1]:
        for eq in eqs:
            st.latex(myprint2(eq))
st.divider()

gamma = st.session_state[str(fres)]/st.session_state[str(fsw)]*np.pi
K = st.session_state[str(Q)]*gamma/2
st.latex(r'\gamma = \pi \frac{f_{res}}{f_{sw}} = \,' + f'{gamma:.2f}')
s = r'\text{K} = \frac{Q\cdot \gamma}{2} =' + \
    r'\frac{\omega_{res} L_{res}}{R_L}\frac{f_{res}\pi}{f_{sw}2} =' + \
    r'\frac{1}{w_{res}R_L C_{res}}\frac{\omega_{res}/2\pi \cdot \pi}{f_{sw}/2}='+\
    r' \frac{\pi}{2R_L C_{res}\omega_{sw}}= '
st.latex(s + f'{K:.2f}')

st.divider()

Tres = 2*np.pi/st.session_state[str(wres)] #wres = 2*pi/Tres
n = math.floor(st.session_state[str(Tsw)]/Tres)

if n%2 ==0: #even type 

    st.latex(r'\text{even type n dcm:\,} n < \frac{f_{res}}{f_{sw}}=\,' +\
             r'\implies n = \lfloor \frac{f_{res}}{f_{sw}} \rfloor = ' +\
             f'{n}')

    M = n/K
    st.latex(r'M = \frac{n}{K} = \frac{2n}{Q\pi} = ' + f'{n/K:.3f}' +\
             r'\text{,\,n even}')
    #Vcp = Vg*(2-2*n/K+n**2/K)
    #Vc1 = -n*M*Vg         
        
else: 
    st.latex(r'\text{odd type n dcm:\,} n < \frac{f_{res}}{f_{sw}}=\,' +\
             r'\implies n = \lfloor \frac{f_{res}}{f_{sw}} \rfloor = ' +\
             f'{n}')


st.divider()
s = r'\text{even  +type n ccm:}\, \frac{1}{n+2} < \frac{f_{sw}}{f_{res}} < '+\
    r'\frac{1}{n+1} \implies n > \frac{f_{res}}{f_{sw}}-1  ' +\
        r'\implies n = \lceil \frac{f_{res}}{f_{sw}}-1 \rceil = '
n = math.ceil(st.session_state[str(fres)]/st.session_state[str(fsw)] -1)
st.latex(s + f'{n}')

nlb = st.session_state[str(fres)]/st.session_state[str(fsw)] -1
nub = st.session_state[str(fres)]/st.session_state[str(fsw)]
s = r'\text{even -type n ccm:}\, \frac{1}{n+1} < \frac{f_{sw}}{f_{res}} < '+\
    r'\frac{1}{n} \implies ' +\
    r'\frac{f_{res}}{f_{sw}} - 1 < n < \frac{f_{res}}{f_{sw}} \implies '+\
            f'{nlb:.3f}'+ r' < n < '+ f'{nub:.3f}' 
st.latex(s )


st.divider()





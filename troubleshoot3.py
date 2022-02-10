#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 07:12:36 2022

@author: erik
"""
from sympy.core.symbol import symbols, Symbol
from itertools import repeat, product
from orderedset import OrderedSet
import math 
a, b, c, d, f = symbols('a b c d f')
exp1 = c + d - f
exp2 = a*b - c

ad = {a : set([a-0, c/b]), b : set([b-0, c/a]), c:set([c-0, b/a]),
      d: set([d - 0 , f-c]),f:set([f-0, c+d]) }
#ad = {a : OrderedSet([]), b : OrderedSet([4,5]), c:OrderedSet([6]) }
ad_keys = ad.keys()
ad_vals = ad.values()

def get_combos(want, vals):
    '''

    Parameters
    ----------
    vals : the values of a dictionary. The values are 
        OrderedSets of expressions for variables

    Returns
    -------
    Unique combinations of variables from all the values,
    all of which exclude the variable being solved for.
    The idea is that for an expression 
    z = f(x,y), if you substitute in expressions for 
    x and y in turn, as x=f(a,b) and y=f(c,d),
    you will get the same result as substituting 
    x = f(a,c), y=f(b,d) because ultimately 
    z=f(a,b,c,d) is unique. 

    '''
   
    #def samesymbols(expr1, expr2):
    #    return expr1.atoms(Symbol) == expr2.atoms(Symbol) 
    #def havecomboyet():
    #    return
 
    def addifunique(product):
        '''
                Parameters
        ----------
        product : TYPE
            DESCRIPTION.

        Returns
        -------
        list
            DESCRIPTION.
            
        

        '''
        myM = Symbol('M', real=True)
        myD = Symbol('D', real=True, positive=True) 
       
        unique_combos = []
        
        setofsymbolssets = set()
        for combo in product: 
            a = set()
            for expr in combo: 
                a |= expr.atoms(Symbol)
            a = frozenset(a)
            boolop = (myM in a) and (myD in a)
            #print(a)
            if a not in setofsymbolssets and want not in a and not boolop:
                print(a)
                setofsymbolssets.add(a)
                unique_combos.append(combo)
        return unique_combos
    
    '''
    def getsetofsymbolssets(product):
                  
        
        

        Parameters
        ----------
        product: an iterable of combinations of 
            substitution expressions . 
            Each combination is a tuple
            The tuples are tuples of new expressions that 
            could be substituted as in 
            [(old1, new1), (old2, new2), ...]

        Returns
        -------
        a set of sets, each set is a unique combination 
        of variables to form new1, new2, ... substitutions

        
        setofuniquecombos = set()
        for tup in product:
            tupsetofsymbols = set()
            for expr in tup:
                tupsetofsymbols |= expr.atoms(Symbol)
            setofuniquecombos.add(tupsetofsymbols)
        return setofuniquecombos
    '''
    #setofsymbolsets = getsetofsymbolssets(product(*vals))
    #unfiltered_combos = product(*vals) 
    unique_combos = addifunique(product(*vals))
    
    return unique_combos

    
    '''
    
    while true: 
        
    
    
    for os in list(vals):
        for expr in os:
            if want in [expr]: 
                os.remove(expr)
    return product(*vals)
    '''
combos = get_combos(b, ad_vals)
#combos = product(*ad_vals)
subs = [zip(ad_keys, combo) for combo in combos]



'''
construct all possible (old,new) pairs in lists: 
[(a, 1), (b,4), (c,6)]
[(a, 2), (b,4), (c,6)]
[(a, 3), (b,4), (c,6)]
[(a, 1), (b,5), (c,6)]
[(a, 2), (b,5), (c,6)]
[(a, 3), (b,5), (c,6)]

'''

#def get_combos(ad_vals):
#    print(*ad_vals)
    
#    return product(*ad_vals)


for el in subs: 
    print(*el)
    
aset = OrderedSet([a])
bset = OrderedSet([a])

def get_num_reps(num_vars):
    s = 0
    for i in range(2, num_vars):
        s += math.comb(num_vars, i)
    return s 
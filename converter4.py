#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 07:51:07 2021

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
from sympy.printing import latex, pprint, pretty
from sympy import simplify# Symbol, 

import logging

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
        
    s = f'$${latex(args[0])} {helper(args[1:])}$$' 
    display(Latex(s))   
    
def myprint2(eq):
    #if isinstance(eq2.func, sympy.core.add.Add):
    if eq.func == sympy.core.add.Add:
        lhs = eq.args[0]
        rhs = -1*eq.args[1]
        myprint(lhs, rhs)
    else:
        print('didnt work')
    return

def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator



class variable(sympy.core.symbol.Symbol):
    def __new__(self, name, *args, **assumptions):
        obj = Symbol.__new__(self, name, **assumptions )
        obj.altname = args[1] if len(args)>1 else None
        obj.unit = args[0] if len(args)>0 else ''
        return obj
    
    def __str__(self):
        if self.altname is not None: 
            return self.altname
        else: 
            return super().__str__()


class NotUniqueError(Exception):
    pass
'''
def p(s, indents=''):
    return '\n' + indents + pretty(s, use_unicode=True).replace('\n', '\n'+indents)
'''
class converter:
 
    def __init__(self):
        self.equations = OrderedSet([]) #expressions assumed to = 0 (Sympy convention)
        self.relations = {} # useful symbolic expressions that are solved for
        self.variables = set()
        self.logger = logging.getLogger('__main__')
        self.debug = self.logger.debug
        self.info = self.logger.info 
        self.flag = 0
        
    def p(self, s):
        indents = '\t'*self.flag
        return '\n' + indents + pretty(s, use_unicode=True).replace('\n', '\n'+indents)

    def showequations(self):
        for eq in self.equations:
            myprint2(eq)
    
    def run_solveset(self, given, want):
        '''
        

        Parameters
        ----------
        given : substitutions to be made, if any
        want : the symbol being solved for

        Returns
        -------
        an ordered set of solutions for wanted symbol

        '''
        eqs = self.equations.copy()
        rhss = OrderedSet([])
        for eq in eqs:
            #go through each equation individually with solveset
            
            temp = solveset(eq.subs(given), want) 
            if type(temp) == sympy.sets.fancysets.Complexes:
                #after substituting known values, eq may be reduced to zero. 
                #and solveset returns the entire set of complex numbers. 
                continue
            self.debug(f'{self.p(eq)} solved for {self.p(want)}={self.p(temp)}')
            if isinstance(temp, sympy.sets.sets.Complement):
                temp = temp.args[0]
            
            if len(temp) ==0: #happens when symbol being solved for isn't in this equation
                continue #meant to get to next pass in for loop
            else: 
                sol = simplify(temp.args[0])
                rhss.add(sol)
                #syms.add(sorted(sol.atoms(Symbol), key=lambda f: f.__str__()))
                #self.info(f'{p(eq)} solved for {p(want)}={p(sol)}')
                #is wanted symbol guaranteed not to be in syms? 
                
        return rhss
    
    def run_nonlinsolve(self, given, want):
        '''
        

        Parameters
        ----------
        given : TYPE
            DESCRIPTION.
        want : TYPE
            DESCRIPTION.

        Returns
        -------
        a solution equal to want

        '''
        eqs = self.equations.copy()
        rhs_tuple = nonlinsolve([eq.subs(given) for eq in eqs], want).args[0]
        # ^ solveset will always return a FiniteSet of solutions for the single variable it can solve for.
        #nonlinsolve will always return a FiniteSet with a single ordered tuple, see documentation ^
        self.debug(f'nonlinsolve returns: {self.p(rhs_tuple[0])}')
        if len(rhs_tuple) != 1:
            raise NotUniqueError
        return rhs_tuple[0]

    def run_solvers(self, given, want):
        '''
        

        Parameters
        ----------
        given : TYPE
            DESCRIPTION.
        want : TYPE
            DESCRIPTION.

        Returns
        -------
        a set combination of the return value of nonlinsolve and solveset

        '''
        self.debug(f'looking for {self.p(want)}')
        rhs = self.run_nonlinsolve(given, want)

        rhss = self.run_solveset(given, want)
        rhss.add(rhs)
        
        return rhss
   
    def solver(self, given, want):
        '''
        Parameters
        ----------
        eqs: a list of symbolic equations
        given: a dictionary of symbol:numeric value pairs, if any
        want: the symbol to solve for, if possible

        Returns
        --------
        the given values are substituted into the equations, and then Sympy's nonlinsolve
        is called. 
        '''
        '''
        s = '\t'
        
        def p(s):            
            new_s = pretty(s, use_unicode=True)
            return '\n' + indents + new_s.replace('\n', '\n'+indents)

        '''
     
        rhss = self.run_solvers(given, want)
        self.debug(f'Done with {self.p(want)}')
        newrhss = set()

     
        syms = set()
        for sol in rhss:
            syms |= sol.atoms(Symbol)
        
        ad = {}
        for sym in syms:
            self.flag +=1
            ad[sym] = self.run_solvers(given, sym)
        
        #1. get the substitutions for each symbol
        #2. substitute each substitution in each solution
        for sol in rhss:
            
            for sym in sol.atoms(Symbol):
                
                for newsub in ad[sym]:
                    newrhss.add(simplify(sol.subs(sym,newsub)))

        myM = variable('M', real=True)
        myD = variable('D', real=True, positive=True)  
        for eq in newrhss.copy():
            syms = eq.atoms(Symbol)
            #self.debug(f'sym list: {p(syms)}')
            boolop = (myM in syms) and (myD in syms)
            #self.debug(f'bool op = {boolop}')
            if (want in syms) or boolop  :
                newrhss.remove(eq)
                #self.info(f'{indents}removing {p(eq)}')
         
        toreturn = rhss.union(newrhss) 
        #self.debug(f'returning: {p(toreturn)}')
     
        self.addnewrelation(want, list(toreturn) )
        return toreturn
    
    def addnewrelation(self, sym, solutions):
        '''
        The relations dictionary is key= symbol, value=set of expressions that calculate value of symbol
                
        '''

        funcs = list()
        for exp in solutions: 
            syms = list(exp.atoms(Symbol))
            mapping = {sym: Symbol(sym.altname) for sym in syms if sym.altname is not None}
            args = [sym.altname if sym.altname is not None else sym for sym in syms]
            funcs.append(lambdify(args, exp.xreplace(mapping), 'numpy' )) 
            #warnings show when you call a function with a set ^
        self.relations[sym] = funcs
        return 
    
    def computesym(self, sym, given):
        '''
        Parameters
        ----------
        sym: a "lhs" symbol, which is a key to the funcs set of functions
        given: 
        '''
        def use_args(have, needed):
            '''
            

            Parameters
            ----------
            have : dictionary of everything that was given with values
            needed : tuple of arguments needed

            Returns
            -------
            a selection of 'have', with no unneeded arguments. 
            Lambdify generated functions won't ignore unneccesary arguments, 
            and the function will raise a KeyError (need to verify?)

            '''
            return {x:have[x] for x in needed}
                
        #lambdify_generated functions must have strings for keyword arguments
    
        temp = dict((key.__str__(), value) for (key, value) in given.items())
        #print(temp)
        
        #print(self.relations[sym])
        for exp in self.relations[sym]:
            #print(exp)
            needed = exp.__code__.co_varnames
            #print(needed)
            try: 
                use = use_args(temp, needed)
                #print(use)
            
            except KeyError:
                continue #don't bother any more with this exp
            
            #try:
              
            return exp(**use)
 
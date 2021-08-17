#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 06:47:52 2021

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
from sympy import Symbol, simplify

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

class variable(Symbol):
    def __init__(self):
        return 

class NotUniqueError(Exception):
    pass

#def p(s):
#    return '\n' + pretty(s, use_unicode=True)
#def p(s, indents=''):
#    return '\n' + indents + pretty(s, use_unicode=True).replace('\n', '\n'+indents)

class BuckBoost:
 
    def __init__(self):
        self.equations = OrderedSet([]) #expressions assumed to = 0 (Sympy convention)
        self.relations = {} # useful symbolic expressions that are solved for
        self.variables = set()
        self.logger = logging.getLogger('__main__')
        self.debug = self.logger.debug
        self.info = self.logger.info 
        

    def showequations(self):
        for eq in self.equations:
            myprint2(eq)

   
    def solver(self, given, want, recursesym=None):
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
        s = '\t'
        
        def p(s):            
            new_s = pretty(s, use_unicode=True)
            return '\n' + indents + new_s.replace('\n', '\n'+indents)

        try:
            if want in recursesym:
                self.debug(f'{s*len(recursesym)}base case')
                return set()
            
        except TypeError:
            recursesym = []
        #used for recursive logging visibility:
        indents = s*len(recursesym)
        self.debug(f'{indents}adding {want} to {recursesym}')
        recursesym.append(want)
        eqs = self.equations.copy()
        #try all equations together first
        rhs_tuple = nonlinsolve([eq.subs(given) for eq in eqs], want,).args[0]
        # ^ solveset will always return a FiniteSet of solutions for the single variable it can solve for.
        #nonlinsolve will always return a FiniteSet with a single ordered tuple, see documentation ^
        self.debug('{}nonlinsolve returns: {}'.format(indents,p(rhs_tuple) ))
        if len(rhs_tuple) != 1:
            raise NotUniqueError
        rhs = rhs_tuple[0]

        rhss = OrderedSet([rhs])
        #nonlinsolve only returns the first solution it finds. There may be other useful ones too. 


        for eq in eqs:
            #go through each equation individually with solveset
            
            temp = solveset(eq.subs(given), want) 
            if isinstance(temp, sympy.sets.sets.Complement):
                temp = temp.args[0]
            
            if len(temp) ==0: #happens when symbol being solved for isn't in this equation
                continue #meant to get to next pass in for loop
            else: 
                rhss.add(simplify(temp.args[0]))
            self.info(f'{p(eq)} solved for {p(want)}={p(temp)}')
         

        '''
        substitute a solution for a into c = a/b
        and/or a solution for b in c= a /b

        '''
        #this function returns a set of solutions for a symbol
        #call it again 
        self.debug(f'{indents}so far {want} = {p(rhss)}')
        newrhss = OrderedSet([])
        for sol in rhss:
            self.debug(f'{indents}solution to {want} is: {p(sol)} ')
            '''
            make this next line repeatable!
            '''
            myset = sol.atoms(Symbol)
            mysorted = sorted(myset, key=lambda f: f.__str__())
            #self.debug(f'set of syms: {myset}')
            #self.debug(f'ordered: {mysorted}')
            
            #ordered = OrderedSet(myset)
            #self.debug(f'orderedset: {ordered}')
            #for sym in ordered:
            for sym in mysorted:
                #if len(recursesym) == 
                self.debug(f'recursesym: {p(recursesym)}')
                #if indents == '' and len(recursesym > 0):
                #    recursesym=[]
                self.debug(f'{indents}calling solver looking for {p(sym)}')
                for newsub in self.solver(given, sym, recursesym=recursesym):
                    
                    new = sol.subs(sym, newsub)
                    newrhss.add(simplify(new))
                    
                    self.debug(f'{indents}sub-ing in {p(newsub)} for {p(sym)}')
                    self.debug(f'{indents}and found {p(new)}')
                    
        myM = symbols('M', real=True)
        myD = symbols('D', real=True, positive=True)  
        for eq in newrhss.copy():
            syms = eq.atoms(Symbol)
            #self.debug(f'sym list: {p(syms)}')
            boolop = (myM in syms) and (myD in syms)
            #self.debug(f'bool op = {boolop}')
            if (want in syms) or boolop  :
                newrhss.remove(eq)
                self.info(f'{indents}removing {p(eq)}')
         
        toreturn = rhss.union(newrhss) 
        self.debug(f'end of function, recursesym: {recursesym}')
        self.debug(f'returning: {p(toreturn)}')
        if want == recursesym[0]:
            self.addnewrelation(want, list(toreturn) )
        return toreturn
    
    def addnewrelation(self, sym, solutions):
        '''
        The relations dictionary is key= symbol, value=set of expressions that calculate value of symbol
                
        '''
        funcs = list()
        for exp in solutions: 
            funcs.append(lambdify(list(exp.atoms(Symbol)), exp, 'numpy' )) 
            #warnings show when you call a function with a set ^
        self.relations[sym] = funcs
        return 
    
    def computesym(self, sym, given):
        '''
        Parameters
        ----------
        sym: a "lhs" symbol, which is a key to the funcs set of functions
        '''
        for exp in self.relations[sym]:
            try:
                #lambdify_generated functions must have strings for keyword arguments
                temp = dict((key.__str__(), value) for (key, value) in given.items())
                return exp(**temp)
            except KeyError:
                pass
            except TypeError:
                pass
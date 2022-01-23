#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 18:19:03 2022

@author: erik
"""



from IPython.display import display, Latex
from functools import wraps
from itertools import product
from copy import deepcopy
from orderedset import OrderedSet
import sympy
from sympy.core.symbol import symbols, Symbol
from sympy.solvers.solveset import nonlinsolve
from sympy import solveset
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
        rhs = eq - lhs
        myprint(-1*lhs, rhs)
    else:
        print('didnt work')
    return

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
    

    '''
    
    return product(*vals)

def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator

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
        myM = variable('M', real=True)
        myD = variable('D', real=True, positive=True) 
       
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
                #print(a)
                setofsymbolssets.add(a)
                unique_combos.append(combo)
        return unique_combos
    
    unique_combos = addifunique(product(*vals))
    return unique_combos

    

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
            #self.debug(f'{self.p(eq)} solved for {self.p(want)}={self.p(temp)}')
            if isinstance(temp, sympy.sets.sets.Complement):
                temp = temp.args[0]
            
            if len(temp) ==0: #happens when symbol being solved for isn't in this equation
                continue #meant to get to next pass in for loop
            else: 
                sol = simplify(temp.args[0])
                rhss.add(sol)

                
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
        #self.debug(f'nonlinsolve returns: {self.p(rhs_tuple[0])}')
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
                self.flag -= 1
                self.debug(f'{s*len(recursesym)}base case')
                self.debug(f'returning: {want}={pretty(recursesym[want])}')
                return recursesym[want]
            
        except TypeError:
            recursesym = {}
        #used for recursive logging visibility:
        indents = s*len(recursesym)
        self.flag += 1
        self.debug(f'{indents}adding {want} to {list(recursesym)}')
        if want not in recursesym:
            recursesym[want] = set()
        
        rhss = self.run_solvers(given, want)
        self.debug(f'{indents}Done with {self.p(want)}')
        self.debug(f'{indents}so far {want} = {p(rhss)}')
        

        newrhss = OrderedSet([]) #newrhss will be the solutions found already (nonrecursively)
        # and then also those found recursively. 
        
        
        for sol in rhss:

            syms = sol.atoms(Symbol)
            syms = sorted(syms.copy(), key=lambda f: f.__str__())
            for sym in syms:
    
                self.debug(f'{indents}recursesym: {p(list(recursesym))}')
                self.debug(f'{indents}calling solver looking for {p(sym)}')
                #if sym is already in recursesym, it'll hit the base case

                solutions = self.solver(given, sym, recursesym=recursesym)
                recursesym[sym] |= solutions #recursesym[sym] is one or more expression
                #that can be substituted for sym in sol
                #call a function that makes a substitution, removes that expression, 
                #and returns an empty set if there are no more substitutions to make, 
                #or recurse and make additional substitutions 
                #to make multiple substitutions at once, pass a list of (old, new)
                #pairs 
                recursesym[sym] |= OrderedSet([sym]) #makes substitutions easier later
            self.debug(recursesym) 
            #only make combinations of symbols that 
            #are actually in sol. Otherwise it'll be a 
            #worthless substitution and get thrown out. 
            needed = {sym: recursesym[sym] for sym in syms}
            keys = needed.keys()
            vals = needed.values()
            #combos = product(*vals)
            combos = get_combos(want, vals)
            self.debug(list(keys))
            self.debug(list(vals))
            subs = [zip(keys, combo) for combo in combos]
            self.debug(f'number of subs = {len(subs)}')
            self.debug(f'{indents}solution to {want} is: {p(sol)} ')

            for sub in subs:

                log_sub= deepcopy(sub)
                #we may already have a given combination 
                # of variables in an expression.
                #only substitute a given combination 
                #of variables ONCE
                new = sol.subs(list(sub))
                newrhss.add(simplify(new))
                
                self.debug(f'{indents}sub-ing in {list(log_sub)}')
                self.debug(f'{indents}and found {p(new)}')
     
        toreturn = rhss.union(newrhss) 
        self.debug(f'end of function, recursesym: {recursesym}')
        self.debug(f'returning: {p(toreturn)}')
        
        if want == list(recursesym)[0]: 
            self.addnewrelation(want, list(toreturn) )
        return toreturn
    
    def addnewrelation(self, sym, solutions):
        '''
        The relations dictionary is key= symbol,
        value=set of expressions that calculate value of symbol
                
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
 
    
    def showresult(self, var, given):
         '''
         Parameters
         ----------
         var : a variable of this converter. 
         given: a dictionary of symbol:numeric value pairs 

         Side effects: 
             displays the variable, its value, and units 
         Returns
         -------
         None.

         '''
         result = self.computesym(var, given)
         myprint(var, f'{result:.3f} {var.unit}')
         
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 11:42:08 2022

@author: erik
"""
from sympy.printing import pretty
flag = 1

ans= '⎧c⎫\n⎨─⎬\n⎩b⎭'
text1 = 'a⋅b - c'
text2 = ' solved for '
text3 = 'a'
text4 = ' = '
# =============================================================================
# def p(*args):
#     '''
#     first arg: sympy object
#     second arg: string 
#     '''
#     def helper(*args, chars=0):
#         if len(args) == 0:
#             return ''
#         print(f'chars start = {chars}')
#         ret_str= pretty(args[0], use_unicode=True)
#         indent_ret_str = ret_str.replace('\n', '\n'+indents+' '*chars)
#         chars = len(indent_ret_str.expandtabs())
#         print(f'chars end = {chars}')
#         return indent_ret_str + helper(*args[1:], chars=chars)
#     indents = '\t'*flag
#     return indents + helper(*args)#, chars = 4)
# =============================================================================
def p(*args):
    '''
    first arg: sympy object
    second arg: string 
    '''
    def helper(*args, chars=0):
        if len(args) == 0:
            return ''
        print(f'chars start = {chars}')
        ret_str= pretty(args[0], use_unicode=True)
        ret_str = ret_str.replace('\n', '\n'+' '*(chars))
        charsend = len(ret_str)
        print(f'chars end = {charsend}')
        indent_ret_str = ret_str.replace('\n', '\n'+indents)
        return indent_ret_str + helper(*args[1:], chars=chars+ charsend)
    indents = '\t'*flag
    return indents + helper(*args)#, chars = 4)
print(p(text1, text2, text3, text4, ans))
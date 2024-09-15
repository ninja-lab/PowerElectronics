#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 07:20:13 2024

@author: erik
"""
class Quantity:
    def __init__(self, value, unit, latex_name):
        self.value = value
        self.unit = unit
        self.latex_name = latex_name
        self.formatted_latex = f"${latex_name} = {value:.2f}\;{unit}$"
    
    def __add__(self, other):
        if isinstance(other, Quantity):
            if self.unit == other.unit:
                result_value = self.value + other.value
                result_latex_name = f"({self.latex_name} + {other.latex_name})"
                return Quantity(result_value, self.unit, result_latex_name)
            else:
                raise ValueError("Units must be the same to add quantities.")
        else:
            raise TypeError("Can only add Quantity objects.")
    
    def __mul__(self, other):
        if isinstance(other, Quantity):
            result_value = self.value * other.value
            result_unit = f"{self.unit}*{other.unit}"
            result_latex_name = f"({self.latex_name} \\cdot {other.latex_name})"
            return Quantity(result_value, result_unit, result_latex_name)
        elif isinstance(other, (int, float)):
            result_value = self.value * other
            return Quantity(result_value, self.unit, self.latex_name)
        else:
            raise TypeError("Can only multiply by Quantity objects or numeric values.")
    
    def __repr__(self):
        return f"Quantity(value={self.value}, unit='{self.unit}', latex_name=r'{self.latex_name}')"

# Example usage
if __name__ == "__main__":
    q1 = Quantity(10, "V", r"C_{res}")
    q2 = Quantity(20, "V", r"f_{sw}")
    q3 = q1 + q2
    q4 = q1 * q2
    q5 = q1 * 2

    print(q1.formatted_latex)  # $C_{res} = 10.00\;V$
    print(q2.formatted_latex)  # $f_{sw} = 20.00\;V$
    print(q3.formatted_latex)  # $(C_{res} + f_{sw}) = 30.00\;V$
    print(q4.formatted_latex)  # $(C_{res} \cdot f_{sw}) = 200.00\;V*V$
    print(q5.formatted_latex)  # $C_{res} = 20.00\;V$

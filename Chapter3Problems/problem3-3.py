#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 16:33:12 2020
Fundamentals of Power Electronics problem 3.3
@author: erik
"""
    
import numpy as np
import pandas as pd
import sys
sys.path.append('/home/erik/Documents/ngspice_ckts/ngspice_read')
import ngspice_read
import matplotlib.pyplot as plt

D= np.linspace(0, 1, 100)

#Rl = 
#Rload = 1
ratio = np.array([.001, .002, .01, .02])
#ratio = np.array([.001])
fig3, ax3 = plt.subplots(subplot_kw={'title':'Efficiency vs Duty Cycle'})
#M = (2*D-1)/((2*D-1)**2+Rl/Rload)
fig, ax = plt.subplots(subplot_kw={'title':'M(D) of current fed bridge inverter'})
for r in ratio:    
    M = (2*D-1)/((2*D-1)**2+r)
    eta = ((2*D-1)**2)/((2*D-1)**2+r)
    ax.plot(D, M)
    ax3.plot(D, eta)

#plotlist = ngspice_read.ngspice_read('/home/erik/Documents/ngspice_ckts/rawspice.raw').get_plots()
#spiceplot = plotlist[0]
#ax.plot(spiceplot.get_datavector('vc1').get_data(), spiceplot.get_datavector('m').get_data())    
df = pd.read_table('/home/erik/Documents/Education/powerelectronics/AdvancedConverterControlTechniques/HBridgeDraf5.txt')   
print(df.columns)
#print(plotlist['d'])
ax3.plot(df['d'], df['V(vc)']*df['I(R2)']/(df['V(vg)']*df['I(R1)']) , marker='*')
ax.grid(b=True)
ax.set_xlabel('Duty Cycle')
ax.set_ylabel('Conversion Ratio M(D)')
ax.set_ylim(bottom=-20, top = 20)
#ax.set_xlim(left=.499, right=.501)

#fig2, ax2 = plt.subplots(subplot_kw={'title':'Vout vs time'})
#x = spiceplot.get_scalevector().get_data()
#ax2.plot(x, spiceplot.get_datavector('vout').get_data())   



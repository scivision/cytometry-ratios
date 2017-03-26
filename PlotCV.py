#!/usr/bin/env python
"""
Various plots for Coefficient of Variation, loaded from HDF5
"""
from pathlib import Path
from numpy import median,arange,append
from skimage.filters import gaussian
from matplotlib.pyplot import figure,show
import h5py
import seaborn
seaborn.set_style('ticks')

LVL = append(arange(1.0,2.0,.1),arange(2.,6.,.2))
#LVL=10
CVminmax = [1,10]

def loadcv(fn):
    fn = Path(fn).expanduser()
    with h5py.File(fn,'r') as f:
        for p in f: #for each variable in file
            plotcv(f[p],p)
        

def plotcv(dat,name):
    
    D = gaussian(dat,17) #smoothed for contour
    
  
    fg = figure()
    ax = fg.gca()
    hi=ax.imshow(dat,cmap='cubehelix_r',origin='bottom',
                 vmin=CVminmax[0],vmax=CVminmax[1])
    fg.colorbar(hi).set_label('CV %')
    hc = ax.contour(D,LVL,colors='k')
    ax.clabel(hc,fmt='%0.1f')
    
    ax.set_title(f'{name}\nmin(CV)={D.min():.2f} %'
                 f'  median(CV)={median(D):.2f} %'
                 f'  mean(CV)={D.mean():.2f} %')
  


    
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='HDF5 filename containing CV measurements.')
    p = p.parse_args()
    
    loadcv(p.fn)
    
    show()

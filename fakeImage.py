#!/usr/bin/env python
"""
@author: greg
"""
from matplotlib.pyplot import subplots,show
import numpy as np
#
from pycyto import nuclei,illum,doccl

Nbits=12
Nnuc = 50
led_angle = 30*np.pi/180 #degrees
distance_to_led = .1 #meters
slide_size = .02 #meters
Nxy = (512,512)

bitdepth=2**Nbits-1
dtype=np.uint16

AT1 = .8
AT2 = .6


def simout(uv,blue):
    fg,axs = subplots(1,2,sharex=True,sharey=True,figsize=(14,5))

    ax = axs[0]
    h=ax.pcolormesh(uv,cmap='Purples_r')
    fg.colorbar(h,ax=ax)
    ax.set_title('UV excitation')
    ax.autoscale(True,tight=True)

    ax = axs[1]
    h=ax.pcolormesh(blue,cmap='Blues_r')
    fg.colorbar(h,ax=ax)
    ax.set_title('blue excitation')
    ax.autoscale(True,tight=True)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-e','--ext',help='file extension to glob [default .png]',default='.png')
    p.add_argument('-m','--aparam',help='analysis parameters e.g. "wiener"',nargs='+',default=[None])
    p.add_argument('-p','--plot',help='plot types to make [raw thres rawthres rawcentroid]',default=[],nargs='+')
    p.add_argument('-t','--thres',help='Otsu threshold scaling factor [0.75]',default=0.75,type=float)
    p.add_argument('-r','--centrad',help='radius about cell center to sum',type=int,default=3)
    p.add_argument('-o','--odir',help='directory to save results')
    p.add_argument('-v','--verbose',action='count',default=0)
    p = p.parse_args()

    P = {'param':p.aparam,
         'makeplot':p.plot,
         'odir':p.odir,
         'ext':p.ext,
         'thres':p.thres,
         'centrad':p.centrad,
         'verbose':p.verbose,
         'erode':False
        }

    im = nuclei(Nxy,Nnuc,dtype,bitdepth)
    uv,blue = illum(im,slide_size,Nxy,AT1,distance_to_led,led_angle,p.verbose)

    simout(uv,blue)

    uv_sum,centroids = doccl(uv,None,'',P)
    blue_sum = doccl(blue,centroids,'',P)[0]
#%% estimation
    """
    X/(X + Y) <> .8 falciparum
                 .6 non-falciparum

    """


    ratio = uv_sum/blue_sum


    show()
#!/usr/bin/env python
"""
Forward model for Whole Slide Cytometry with diluted whole blood
"""
from numpy import zeros,count_nonzero
from skimage.util import random_noise
from matplotlib.pyplot import figure,show

BITS=12

def nuclei(Nx,Ny,cellpct):

    im = zeros((Ny,Nx),dtype='uint16')
    im = random_noise(im,'s&p',amount=2*cellpct/100) * (2**BITS - 1)

    return im


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('--nx',type=int,default=1280,help='xpixels')
    p.add_argument('--ny',type=int,default=960,help='ypixels')
    p.add_argument('--pct',type=float,default=5,help='percent of pixels with cells')
    p = p.parse_args()

    im = nuclei(p.nx, p.ny, p.pct)

    print('cells {:.1f} % of pixels'.format(count_nonzero(im)/p.nx/p.ny*100))

    ax = figure().gca()
    ax.imshow(im,cmap='gray',interpolation='none',origin='bottom')
    ax.set_title('noise-free')

    show()
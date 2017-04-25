#!/usr/bin/env python
"""
Plots raw images from whole slide cytometer, more automated than just using ImageJ
Michael Hirsch, Ph.D.

./PlotCytoRawImages.py ~/data/2017-04-24/basler-bare-sensor/
"""
from pathlib import Path
import numpy as np
from skimage.filters import gaussian
from matplotlib.pyplot import figure,show
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
sns.set_style('ticks')
import tifffile

def plotimg(img, fn:Path):
    D = gaussian(img,7)*4096 #smoothed for contour--output is normalized

    fg = figure(figsize=(12,5))
    ax = fg.add_subplot(1,2,1)
    h = ax.imshow(D, cmap='cubehelix', origin='bottom')
    fg.colorbar(h).set_label('data numbers')
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    fg.suptitle(f'{fn.name}')


    x,y = np.meshgrid(range(img.shape[1]), range(img.shape[0]))
    ax = fg.add_subplot(1,2,2,projection='3d')
    #ax.plot_wireframe(x, y, D, rcount=20, ccount=20)
    ax.plot_surface(x, y, D, rcount=20, ccount=20,cmap='cubehelix')
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.set_zlabel('data numbers')


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='HDF5 filename containing CV measurements.')
    p = p.parse_args()

    fn = Path(p.fn).expanduser()
    if fn.is_dir():
        flist = fn.glob('*.tif*')
    elif fn.is_file():
        flist = [fn]
    else:
        raise FileNotFoundError(f'{fn} not a file or directory')

    for fn in flist:
        img = tifffile.imread(str(fn))
        plotimg(img, fn)

    show()

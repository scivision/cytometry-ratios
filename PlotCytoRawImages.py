#!/usr/bin/env python
"""
Plots raw images from whole slide cytometer, more automated than just using ImageJ
Michael Hirsch, Ph.D.

./PlotCytoRawImages.py ~/data/2017-04-24/basler-bare-sensor/
./PlotCytoRawImages.py ~/data/2017-04-24/sumix-bare-sensor/
"""
from pathlib import Path
import numpy as np
import imageio
from skimage.filters import gaussian
from matplotlib.pyplot import figure,show
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
sns.set_style('ticks')
import tifffile

sigma=7

def plotimg(img, fn:Path=None):
    if img.dtype=='uint8':
        bpp=8
    else: # for basler dart ap0134 chip
        bpp=12

    D = gaussian(img,sigma)*(2**bpp-1) #smoothed for contour--output is normalized

    fg = figure(figsize=(12,5))
    if isinstance(fn,Path):
        fg.suptitle(f'{fn.name}', y=0.99)
        zlbl = 'data numbers'
    elif isinstance(fn,str):
        fg.suptitle(fn, y=0.99)
        zlbl = 'normalized'

    ax = fg.add_subplot(1,2,1)
    h = ax.imshow(D, cmap='cubehelix', origin='bottom')
    fg.colorbar(h).set_label(zlbl)
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
# %%
    x,y = np.meshgrid(range(img.shape[1]), range(img.shape[0]))
    ax = fg.add_subplot(1,2,2,projection='3d')
    #ax.plot_wireframe(x, y, D, rcount=20, ccount=20)
    ax.plot_surface(x, y, D, rcount=20, ccount=20,cmap='cubehelix')
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.set_zlabel(zlbl)

    fg.tight_layout()


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('fn',help='HDF5 filename containing CV measurements.')
    p = p.parse_args()

    fn = Path(p.fn).expanduser()
    if fn.is_dir():
        flist = []
        for e in ('*.tif*','*.bmp'):
            flist += fn.glob(e)
    elif fn.is_file():
        flist = [fn]
    else:
        raise FileNotFoundError(f'{fn} not a file or directory')

    for fn in flist:
        if fn.suffix.startswith('.tif'):
            img = tifffile.imread(str(fn))
        else:
            img = imageio.imread(fn)[1:-1,:,0]  # sumix stores all 3 RGB the same values for mono
        plotimg(img, fn)
# %% impulse plot
    imp = np.zeros((72, 72))
    imp[imp.shape[0]//2, imp.shape[1]//2] = 1.

    plotimg(gaussian(imp,sigma),'smoothing kernel')

    show()

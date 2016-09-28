#!/usr/bin/env python
'''
by Michael Hirsch
algorithm:
0. load raw data (eventually 1280x1024 pixel, 10-bit)
1. optional image denoising
2. Otsu threshold method to make binary image based on intensity analysis
3. Morphological operations
4. Connected Component Analysis
5. Property Analysis (Centroid Extraction)
Note: the ccltest() return arguments simply pass out the values from the most recent image, this is trivial to fix if desired
'''
from pycyto import Path
from numpy import zeros_like
from scipy.signal import wiener
from time import time
from matplotlib.pyplot import show
#from guppy import hpy
#
from pycyto import getdata,doratio,dothres,domorph,dolabel

def ccltest(fn,aparam,thresscale,makepl,odir,centRad=3,dbglvl=0):
    if odir:
        odir = Path(odir).expanduser()

    centroid_sum=None #in case no files read
    print('summing centroid radius {} pixels.'.format(centRad))

    for fn in flist:
        fn = Path(fn).expanduser()
        tic = time()
#%% (0) read raw data
        data = getdata(fn,makepl,odir)
        if data is None:
            continue
# setup mask (for results)
        maskdata = zeros_like(data)
#%% (1) denoise
        if 'wiener' in aparam:
            filtered = wiener(data,[5,5]) #TODO puts in negative values
        else:
            filtered = data
#%% (2) threshold (Otsu)
        thres = dothres(data,filtered,thresscale,maskdata,makepl,fn,odir)
#%% (3) morphological ops
        morphed = domorph(data,thres,maskdata,makepl,fn,odir)
#%% (4) connected component labeling
        centroids,nlbl = dolabel(morphed)
#%% (5) property analysis (centroid extraction)
        centroid_sum = doratio(filtered,centroids,nlbl,centRad,makepl,fn,odir)
        print('{:0.2f} sec. to compute {} centroids in {}'.format(time()-tic,nlbl,fn))

    # print(hpy().heap())


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='OpenCV-based cell segmentation')
    p.add_argument('path',help='where image files live. Assumes len()==1: dir to glob. Else list of files',nargs='+')
    p.add_argument('-e','--ext',help='file extension to glob [default .png]',default='.png')
    p.add_argument('-m','--aparam',help='analysis parameters e.g. "wiener"',nargs='+',default=[None])
    p.add_argument('-p','--plot',help='plot types to make [raw thres rawthres rawcentroid]',default=['all'],nargs='+')
    p.add_argument('-t','--thres',help='Otsu threshold scaling factor [0.75]',default=0.75,type=float)
    p.add_argument('--profile',help='cProfile of code',action='store_true')
    p.add_argument('-o','--odir',help='directory to save results')
    p = p.parse_args()

    if len(p.path)==1:
        path = Path(p.path[0]).expanduser()
        if path.is_dir():
            flist = path.glob('*'+p.ext)
        else:
            flist = [path]
    else:
        flist = p.path

    if p.profile:
        try:
            import cProfile as prof
        except ImportError:
            import profile as prof
        from printstats import goCprofile
        profFN = 'ccl.pstats'
        print('saving profile results to', profFN)
        prof.run('ccltest(fn, args.aparam, args.thres, makepl)',profFN)
        goCprofile(profFN)
    else:
        ccltest(flist, p.aparam, p.thres, p.plot,p.odir)

    show()

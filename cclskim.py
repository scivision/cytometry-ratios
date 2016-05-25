#!/usr/bin/env python3
'''
by Michael Hirsch hirsch617@gmail.com
algorithm:
0) load raw data (eventually 1280x1024 pixel, 10-bit)
1) optional image denoising
2) Otsu threshold method to make binary image based on intensity analysis
3) Morphological operations
4) Connected Component Analysis
5) Property Analysis (Centroid Extraction)
Note: the ccltest() return arguments simply pass out the values from the most recent image, this is trivial to fix if desired
'''
useocv=False
if useocv:
    import cv2
from os.path import join,expanduser, basename, splitext
from numpy.ma import masked_where
from numpy import zeros_like, uint8, round, empty
from skimage.io import imread
from skimage.filter import threshold_otsu
from skimage.morphology import disk,erosion,dilation
from skimage.measure import label, regionprops
from skimage.draw import circle
from time import time
#from pdb import set_trace
#from matplotlib.colors import LogNorm
#from matplotlib.ticker import LogFormatterMathtext
#from guppy import hpy

def ccltest(fn,aparam,thresscale,makepl,centRad=3,dbglvl=0):
    centroid_sum=None #in case no files read
    print('summing centroid radius', centRad, 'pixels.')

    for f in fn:
        stem = splitext(basename(f))[0]
        tic = time()
#%% (0) read raw data
        data = getdata(f,makepl,dbglvl)
        if data is None: continue
# setup mask (for results)
        maskdata = zeros_like(data)
#%% (1) denoise
        if 'wiener' in aparam:
            from scipy.signal import wiener
            filtered = wiener(data,[5,5]) #TODO puts in negative values
        else:
            filtered = data
#%% (2) threshold (Otsu)
        thres = dothres(data,filtered,thresscale,maskdata,makepl,f,dbglvl)
#%% (3) morphological ops
        morphed = domorph(data,thres,maskdata,makepl,f,dbglvl)
#%% (4) connected component labeling
        cclbl,nlbl = label(morphed,neighbors=8,return_num=True)
        nlbl -= 1 # labels are one-indexed
#%% (5) property analysis (centroid extraction)
        centroid_sum = doratio(filtered,cclbl,nlbl,centRad,f,makepl,stem,dbglvl)
        print(('{:0.2f}'.format(time()-tic) + ' sec. to compute ' + str(nlbl)+ ' centroids ' + f))
#%% plot
   # print(hpy().heap())
        if makepl[0] is not None:
            show()
    return data, centroid_sum
#================================================================================
def getdata(f,makepl,dbglvl):
    if useocv:
        data = cv2.imread(f,cv2.CV_LOAD_IMAGE_GRAYSCALE) #uint8 data for this example .tif
    else:
        data = imread(f,as_grey=False) # if data is gray integer, maintains that

    if data is None:
        print(f,'not found')
        #centroid_sum = None
        return data
    sy,sx = data.shape #assumes greyscale
    if 'raw' in makepl or 'all' in makepl:
        fg = figure(); ax =fg.gca()
        hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
        fg.colorbar(hi)#,format=LogFormatterMathtext())
        ax.set_title('raw ' + str(data.dtype) + ' data:  ' + f)
        ax.autoscale(True)
    return data

def dothres(data,filtered,thresscale,maskdata,makepl,f,dbglvl):
    if useocv:
        thresval = int(round(thresscale * cv2.threshold(filtered,0,255, cv2.THRESH_OTSU)[0]))
        #we need to modify the Otsu value a little (this is common, see matlab vision.AutoThresholder)
        thres = cv2.threshold(filtered,thresval,255,cv2.THRESH_BINARY)[1]
    else:
        thresval = thresscale * threshold_otsu(filtered)
        thres = filtered > thresval
        
    if dbglvl>0:
        print('Otsu threshold: ' + str(thresval))
    if 'thres' in makepl or 'all' in makepl:
        ax = figure().gca()
        ax.imshow(thres)
        ax.set_title('threshold binary result' + f)
    if 'rawthres' in makepl or 'all' in makepl:
        maskthres = masked_where(thres,maskdata)
        fg = figure(); ax = fg.gca()
        hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
        fg.colorbar(hi)#,format=LogFormatterMathtext())
        ax.imshow(maskthres,cmap = 'jet', interpolation = 'none')
        ax.set_title('thresholded data result  ' + f)
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
    return thres

def domorph(data,thres,maskdata,makepl,f,dbglvl):
    #http://docs.opencv.org/modules/imgproc/doc/filtering.html#void%20erode%28InputArray%20src,%20OutputArray%20dst,%20InputArray%20kernel,%20Point%20anchor,%20int%20iterations,%20int%20borderType,%20const%20Scalar&%20borderValue%29
    erodekernel = disk(2, dtype=uint8)
    if useocv:
        eroded = cv2.erode(thres, erodekernel)
    else:
        eroded = erosion(thres, erodekernel)

    if 'erode' in makepl or 'all' in makepl:
        ax = figure().gca()
        ax.imshow(eroded)
        ax.set_title('erosion binary result' + f)
#%% dilation
    dilatekernel = disk(2, dtype=uint8)
    if useocv:
        dilated = cv2.dilate(eroded,dilatekernel)
    else:
        dilated = dilation(eroded, dilatekernel)
    if 'dilate' in makepl or 'all' in makepl:
        ax = figure().gca()
        ax.imshow(dilated)
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
        ax.set_title('dilation binary result' + f)
    if 'rawdilate' in makepl or 'all' in makepl:
        maskdilate = masked_where(dilated,maskdata)
        fg = figure(); ax = fg.gca()
        hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
        fg.colorbar(hi)
        ax.imshow(maskdilate,cmap = 'jet', interpolation = 'none')
        ax.set_title('dilated data result  ' + f)
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
        print(dilatekernel)
    return dilated

def doratio(data,cclbl,nlbl,centRad,f,makepl,stem,dbglvl):
    #http://scikit-image.org/docs/0.10.x/auto_examples/plot_regionprops.html
    regions = regionprops(cclbl, data, True)
    #preallocate array for centroids (not necessarily the best approach)
    centroid_rc = empty((nlbl,2),dtype=float)
    centroid_sum = empty(nlbl,dtype=int)
    for iReg, region in enumerate(regions):
        centroid_rc[iReg,:] = region.centroid # vs weighted_centroid (want unweighted)
        csi = circle(centroid_rc[iReg,0], centroid_rc[iReg,1], 
                            radius=centRad, shape=data.shape)
        centroid_sum[iReg] = data[csi].sum()
    if 'rawcentroid' in makepl or 'all' in makepl:
        fg = figure(); ax = fg.gca()
        hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
        hc = fg.colorbar(hi)
        hc.set_label('data numbers')
        ax.plot(centroid_rc[:,1],centroid_rc[:,0], 
                marker='.', linestyle='none',color='red',markersize=1)
        ax.set_title('centroids of '+ str(centroid_rc.shape[0]) + ' connected regions  ' + f)
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
        ax.autoscale(True,tight=True)
        if 'png' in makepl:
            fg.savefig('out/' + stem + '_centroid.png',dpi=150,bbox_inches='tight')

    return centroid_sum

# code below is strictly for parsing command-line input
if __name__ == '__main__':
    from argparse import ArgumentParser
    flist = ('FRAME_1457.tif','FRAME_1458.tif','FRAME_1459.tif','FRAME_1460.tif','FRAME_1461.tif','FRAME_1462.tif')

    p = ArgumentParser(description='OpenCV-based cell segmentation')
    p.add_argument('--dir',help='where image files live',default='./data')
    p.add_argument('-m','--aparam',help='analysis parameters e.g. "wiener"',nargs='+',default=[None])
    p.add_argument('infile',help='image data file(s)',nargs='?',default=flist,type=str)
    p.add_argument('-p','--plot',help='plot types to make [raw thres rawthres rawcentroid]',default=[None],nargs='+')
    p.add_argument('-t','--thres',help='Otsu threshold scaling factor [0.75]',default=0.75,type=float)
    p.add_argument('--profile',help='cProfile of code',action='store_true')
    p.add_argument('-s','--saveplot',help='save plots to disk',action='store_true')
    args = p.parse_args()

    dpath = expanduser(args.dir)

    fn = [join(dpath,f) for f in args.infile]

    if args.plot[0] is not None:
        from matplotlib.pyplot import figure, show

    makepl = args.plot
    if args.saveplot:
        makepl.append('png')

    if args.profile:
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
        data, centroid_sum = ccltest(fn, args.aparam, args.thres, makepl)

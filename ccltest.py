#!/usr/bin/env python
'''
by Michael Hirsch michael@scivision.co
algorithm:
0) load raw data
1) optional image denoising
2) Otsu threshold method to make binary image based on intensity analysis
3) Morphological operations
4) Connected Component Analysis
5) Property Analysis (Centroid Extraction)
Note: the ccltest() return arguments simply pass out the values from the most recent image, this is trivial to fix if desired
'''
cvonly = False
from os.path import join,expanduser, basename, splitext
from numpy.ma import masked_where
from numpy import zeros_like, empty,zeros,delete,uint8

if cvonly:
    import cv2
else:
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
        centroids,nlbl = dolabel(morphed)
#%% (5) property analysis (centroid extraction)
        centroid_sum = doratio(data,centroids,nlbl,centRad,makepl,stem,dbglvl)
        print('{:0.2f}'.format(time()-tic) + ' sec. to compute ' +str(nlbl) +'centroids', f)
#%% plot
   # print(hpy().heap())
        if makepl[0] is not None:
            show()
    return data, centroid_sum
#================================================================================
def getdata(f,makepl,dbglvl):
    if cvonly:
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
        hi = ax.imshow(data, cmap='gray',origin='upper', interpolation='none')#, norm=LogNorm())
        fg.colorbar(hi)#,format=LogFormatterMathtext())
        ax.set_title('raw ' + str(data.dtype) + ' data:  ' + f)
        ax.autoscale(True)
    return data

def dothres(data,filtered,thresscale,maskdata,makepl,f,dbglvl):
    if cvonly:
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
        ax.imshow(thres,origin='upper')
        ax.set_title('threshold binary result' + f)
    if 'rawthres' in makepl or 'all' in makepl:
        maskthres = masked_where(thres,maskdata)
        fg = figure(); ax = fg.gca()
        hi = ax.imshow(data, cmap='gray',origin='upper', interpolation='none')#, norm=LogNorm())
        fg.colorbar(hi)#,format=LogFormatterMathtext())
        ax.imshow(maskthres,cmap = 'jet', interpolation = 'none')
        ax.set_title('thresholded data result  ' + f)
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
    return thres

def domorph(data,thres,maskdata,makepl,f,dbglvl):
    '''
    http://docs.opencv.org/modules/imgproc/doc/filtering.html#void%20erode%28InputArray%20src,%20OutputArray%20dst,%20InputArray%20kernel,%20Point%20anchor,%20int%20iterations,%20int%20borderType,%20const%20Scalar&%20borderValue%29
    http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
    http://scikit-image.org/docs/dev/api/skimage.morphology.html#skimage.morphology.disk
    '''

    if cvonly:
        erodekernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        eroded = cv2.erode(thres,erodekernel)
    else:
        erodekernel = disk(2, dtype=uint8)
        eroded = erosion(thres, erodekernel)

    if 'erode' in makepl or 'all' in makepl:
        ax = figure().gca()
        ax.imshow(eroded,origin='upper')
        ax.set_title('erosion binary result' + f)
#%% dilation
    if cvonly:
        dilatekernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        dilated = cv2.dilate(eroded,dilatekernel)
    else:
        dilatekernel = disk(2, dtype=uint8) #scikit-image
        dilated = dilation(eroded, dilatekernel)

    if 'dilate' in makepl or 'all' in makepl:
        ax = figure().gca()
        ax.imshow(dilated,origin='upper')
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
        ax.set_title('dilation binary result' + f)
    if 'rawdilate' in makepl or 'all' in makepl:
        maskdilate = masked_where(dilated,maskdata)
        fg = figure(); ax = fg.gca()
        hi = ax.imshow(data, cmap='gray', origin='upper', interpolation='none')#, norm=LogNorm())
        fg.colorbar(hi)
        ax.imshow(maskdilate,cmap = 'jet',origin='upper', interpolation = 'none')
        ax.set_title('dilated data result  ' + f)
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
    print(erodekernel)
    print(dilatekernel)
    return dilated

def dolabel(data):

    if not cvonly: #use scikit image
        cclbl,nlbl = label(data,neighbors=8,return_num=True)
        nlbl -= 1 # labels are one-indexed
        regions = regionprops(cclbl, data, True)
        centroids = empty((nlbl,2))
        for i,r in enumerate(regions):
            centroids[i,1],centroids[i,0] = r.centroid
    else:
        nlbl = 0
        badind = []
        contours,hierarchy = cv2.findContours(data, 1, 2)
        centroids = zeros((len(contours),2),dtype=int)
        for i,c in enumerate(contours):
            M = cv2.moments(c)
            try:
                centroids[i,0] = int(M['m10']/M['m00'])
                centroids[i,1] = int(M['m01']/M['m00'])
                nlbl += 1
            except ZeroDivisionError:
                #print('skipped i='+str(i))
                badind.append(i)
        centroids = delete(centroids,badind,0)
    return centroids,nlbl

def doratio(data,centroids,nlbl,centRad,makepl,stem,dbglvl):
    ''' http://scikit-image.org/docs/0.10.x/auto_examples/plot_regionprops.html '''
    #preallocate array for centroids (not necessarily the best approach)
    centroid_sum = []

    for crc in centroids:
        if cvonly:
            circletmp = zeros_like(data) #slow!
            cv2.circle(circletmp,(crc[1],crc[0]),centRad,1,thickness=-1)
            csi = circletmp.astype(bool)
        else:
            csi = circle(crc[0], crc[1], radius=centRad, shape=data.shape) #scikit image
        centroid_sum.append(data[csi].sum())
    if 'rawcentroid' in makepl or 'all' in makepl:
        fg = figure(); ax = fg.gca()
        hi = ax.imshow(data, cmap='gray',origin='upper', interpolation='none')#, norm=LogNorm())
        hc = fg.colorbar(hi)
        hc.set_label('data numbers')
        ax.plot(centroids[:,0],centroids[:,1],
                marker='.', linestyle='none',color='red',markersize=2)
        ax.set_title('centroids of '+ str(nlbl) + ' connected regions  ' + f)
        ax.set_xlabel('x-pixel')
        ax.set_ylabel('y-pixel')
        ax.autoscale(True,tight=True)
        if 'png' in makepl:
            fg.savefig('out/' + stem + '_centroid.png',dpi=150,bbox_inches='tight')
    elif 'png' in makepl:
        cv2.imwrite('out/' + stem + '_centroid.png', data)

    return centroid_sum

# code below is strictly for parsing command-line input
if __name__ == '__main__':
    from argparse import ArgumentParser
    flist = ('FRAME_1457.tif','FRAME_1458.tif','FRAME_1459.tif','FRAME_1460.tif','FRAME_1461.tif','FRAME_1462.tif')

    p = ArgumentParser(description='OpenCV-based cell segmentation')
    p.add_argument('--dir',help='where image files live',type=str,default='./data')
    p.add_argument('-m','--aparam',help='analysis parameters e.g. "wiener"',nargs='+',default=[None],type=str)
    p.add_argument('-i','--infile',help='image data file(s)',nargs='+',default=flist,type=str)
    p.add_argument('-p','--plot',help='plot types to make',default=[None],nargs='+',type=str)
    p.add_argument('-t','--thres',help='Otsu threshold scaling factor [0.75]',default=0.75,type=float)
    p.add_argument('--profile',help='cProfile of code',action='store_true')
    p.add_argument('-s','--saveplot',help='save plots to disk',action='store_true')
    args = p.parse_args()

    dpath = expanduser(args.dir)

    fn = [join(dpath,f) for f in args.infile]

    makepl = args.plot
    
    if makepl[0] is not None:
        from matplotlib.pyplot import figure, show

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

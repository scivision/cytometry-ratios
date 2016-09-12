try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path
#
useocv=False
if useocv:
    import cv2
#
from numpy import uint8,  empty
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.morphology import disk,erosion,dilation
from skimage.measure import regionprops
from skimage.draw import circle
#
from .plots import plotraw,plotthres,ploterode,plotdilate,plotcentroid
#%%
def getdata(fn,makepl,odir):
    if useocv:
        data = cv2.imread(fn,cv2.CV_LOAD_IMAGE_GRAYSCALE) #uint8 data for this example .tif
    else:
        data = imread(fn,as_grey=True) # if data is gray integer, maintains that

    if data is None:
        print('{} not found'.format(fn))
        #centroid_sum = None
        return

    sy,sx = data.shape #assumes greyscale
    if 'raw' in makepl or 'all' in makepl:
        plotraw(data,fn,odir)

    return data

def dothres(data,filtered,thresscale,maskdata,makepl,fn,odir):
    if useocv:
        thresval = int(round(thresscale * cv2.threshold(filtered,0,255, cv2.THRESH_OTSU)[0]))
        #we need to modify the Otsu value a little (this is common, see matlab vision.AutoThresholder)
        thres = cv2.threshold(filtered,thresval,255,cv2.THRESH_BINARY)[1]
    else:
        thresval = thresscale * threshold_otsu(filtered)
        thres = filtered > thresval

    print('{}  Otsu threshold: '.format(fn,thresval))

    if 'thres' in makepl or 'all' in makepl:
        plotthres(thres,data,maskdata,fn,odir)

    return thres

def domorph(data,thres,maskdata,makepl,fn, odir):
    #http://docs.opencv.org/modules/imgproc/doc/filtering.html#void%20erode%28InputArray%20src,%20OutputArray%20dst,%20InputArray%20kernel,%20Point%20anchor,%20int%20iterations,%20int%20borderType,%20const%20Scalar&%20borderValue%29
    erodekernel = disk(2, dtype=uint8)
    if useocv:
        eroded = cv2.erode(thres, erodekernel)
    else:
        eroded = erosion(thres, erodekernel)

    if 'erode' in makepl or 'all' in makepl:
        ploterode(eroded,odir)
#%% dilation
    dilatekernel = disk(2, dtype=uint8)
    if useocv:
        dilated = cv2.dilate(eroded,dilatekernel)
    else:
        dilated = dilation(eroded, dilatekernel)
    if 'dilate' in makepl or 'all' in makepl:
        plotdilate(dilated,data,maskdata,dilatekernel,fn,odir)

    return dilated

def doratio(data,cclbl,nlbl,centRad,fn,makepl,odir):
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
        plotcentroid(data,centroid_rc,fn,odir)

    return centroid_sum
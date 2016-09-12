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
from numpy import uint8,  empty,zeros,delete,zeros_like
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.morphology import disk,erosion,dilation
from skimage.measure import regionprops,label
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

    print('{}  Otsu threshold: []'.format(fn,thresval))

    if 'thres' in makepl or 'all' in makepl:
        plotthres(thres,data,maskdata,fn,odir)

    return thres

def domorph(data,thres,maskdata,makepl,fn, odir):
    #http://docs.opencv.org/modules/imgproc/doc/filtering.html#void%20erode%28InputArray%20src,%20OutputArray%20dst,%20InputArray%20kernel,%20Point%20anchor,%20int%20iterations,%20int%20borderType,%20const%20Scalar&%20borderValue%29

    if useocv:
        erodekernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        eroded = cv2.erode(thres,erodekernel)
    else:
        erodekernel = disk(2, dtype=uint8)
        eroded = erosion(thres, erodekernel)

    if 'erode' in makepl or 'all' in makepl:
        ploterode(eroded,fn,odir)
#%% dilation
    if useocv:
        dilatekernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        dilated = cv2.dilate(eroded,dilatekernel)
    else:
        dilatekernel = disk(2, dtype=uint8) #scikit-image
        dilated = dilation(eroded, dilatekernel)

    if 'dilate' in makepl or 'all' in makepl:
        plotdilate(dilated,data,maskdata,fn,odir)

    print(erodekernel)
    print(dilatekernel)

    return dilated

def dolabel(data):

    if not useocv: #use scikit image
        cclbl,nlbl = label(data,neighbors=8,return_num=True)
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

def doratio(data,centroids,nlbl,centRad,makepl,fn,odir):
    centroid_sum = []

    for crc in centroids:
        if useocv:
            circletmp = zeros_like(data) #slow!
            cv2.circle(circletmp,(crc[1],crc[0]),centRad,1,thickness=-1)
            csi = circletmp.astype(bool)
        else:
            csi = circle(crc[0], crc[1], radius=centRad, shape=data.shape) #scikit image
        centroid_sum.append(data[csi].sum())
    if 'rawcentroid' in makepl or 'all' in makepl:
        plotcentroid(data,centroids,fn,odir)

    return centroid_sum
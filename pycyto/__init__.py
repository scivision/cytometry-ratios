try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path
#
if False:
    import cv2
else:
    cv2=None

#
from numpy import uint8,  empty,zeros,zeros_like, arange, fliplr,meshgrid,sqrt,cos,sin,arccos,nan
from numpy.random import rand,poisson
from scipy.signal import wiener
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.morphology import disk,erosion,dilation
from skimage.measure import regionprops,label
from skimage.draw import circle
from scipy.ndimage import gaussian_filter
#
from .plots import plotraw,plotthres,ploterode,plotdilate,plotcentroid,plotillum

def doccl(data,centroids,fn,P):
# setup mask (for results)
    maskdata = zeros_like(data)
#%% (1) denoise
    if 'aparam' in P and 'wiener' in P['aparam']:
        filtered = wiener(data,[5,5]) #TODO puts in negative values
    else:
        filtered = data
#%% (2) threshold (Otsu)
    thres = dothres(data,filtered,maskdata,fn,P)
#%% (3) morphological ops
    morphed = domorph(data,thres,maskdata,fn,P)
#%% (4) connected component labeling
    if centroids is None:
        centroids,nlbl,badind = dolabel(morphed)
    else:
        nlbl = centroids.size
        badind = []
#%% (5) property analysis (centroid extraction)
    centroid_sum = dosum(filtered,centroids,nlbl,badind,fn,P)
    #print('{:0.2f} sec. to compute {} centroids in {}'.format(time()-tic,nlbl,fn))
    return centroid_sum,centroids

def nuclei(Nxy,Nnuc,dtype,bitdepth):
    #set up the image with cell nuclei spots on it
    im = zeros(Nxy,dtype=dtype)
    xpts = (rand(Nnuc)*(Nxy[0]-1)).astype(dtype)
    ypts = (rand(Nnuc)*(Nxy[1]-1)).astype(dtype)

    im[ypts,xpts] = dtype(bitdepth)

    bg = poisson(1,im.shape).astype(dtype)
    im += bg

    im = gaussian_filter(im,1)

    return im

def illum(im,slide_size,Nxy,AT,leddist,ledang,verbose=False):
    """
    calculate distance from led to each pixel, pretty straightforward, just
    use distance formula and assume constant z=0, light intensity decreases
    with the square of the distance to the source

    also calculate angular displacement from center line of LED, the light
    intensity decreases as your angle from the center of the led increases, see
    http://www.ledengin.com/files/products/LZ4/LZ4-04UV00.pdf page 8,
    basically you have to find the angle between two lines, one from the led
    to the center of the stage and the other the line from an arbitrary point
    on the stage to the led. set up 2 vectors and use dot product to find angle
    between vectors

    light intensity decreases at a rate like 1-(x^2)/1.9 if x is radians
    from the center of the led
    """
    X,Y = meshgrid(slide_size/Nxy[0] * arange(-Nxy[0]//2,Nxy[0]//2),
                      slide_size/Nxy[1] * arange(-Nxy[1]//2,Nxy[1]//2))
    distances = sqrt((leddist * sin(ledang))**2
                        +(leddist * cos(ledang)+X)**2
                        +Y**2)

#%% inverse square mask
    invsq = 1/distances**2
    invsq /= invsq[Nxy[1]//2,Nxy[0]//2]

    radiation_pattern = arccos((leddist + X*cos(ledang))/
                                  sqrt(leddist**2 + Y**2+X**2+
                                         2*leddist * X*cos(ledang)))

    Iang = 1 - radiation_pattern**2 / 1.9

    if verbose:
        plotillum(Iang,invsq)

    uv = AT * im * Iang * invsq    # Hoechst 33342 bonds to AT only

    # PicoGreen bonds equally well to AT and GC (it likes dsDNA)
    blue = (AT + (1-AT)) * im * fliplr(Iang * invsq)

    return uv,blue

#%%
def getdata(fn,makepl,odir):

    if cv2 is not None:
        data = cv2.imread(fn,cv2.CV_LOAD_IMAGE_GRAYSCALE) #uint8 data for this example .tif
    else:
        data = imread(fn,as_grey=True) # if data is gray integer, maintains that

    if data is None:
        print('{} not found'.format(fn))
        return

    sy,sx = data.shape #assumes greyscale
    if not set(('raw','all')).isdisjoint(makepl):
        plotraw(data,fn,odir)

    return data

def dothres(data,filtered,maskdata,fn,P):
    if cv2 is not None:
        thresval = int(round(P['thres'] * cv2.threshold(filtered,0,255, cv2.THRESH_OTSU)[0]))
        #we need to modify the Otsu value a little (this is common, see matlab vision.AutoThresholder)
        thres = cv2.threshold(filtered,thresval,255,cv2.THRESH_BINARY)[1]
    else:
        thresval = P['thres'] * threshold_otsu(filtered)
        thres = filtered > thresval

    print('{}  Otsu threshold: []'.format(fn,thresval))

    if not set(('thres','all')).isdisjoint(P['makeplot']):
        plotthres(thres,data,maskdata,fn,P['odir'])

    return thres

def domorph(data,thres,maskdata,fn,P):
    #http://docs.opencv.org/modules/imgproc/doc/filtering.html#void%20erode%28InputArray%20src,%20OutputArray%20dst,%20InputArray%20kernel,%20Point%20anchor,%20int%20iterations,%20int%20borderType,%20const%20Scalar&%20borderValue%29

    if P['erode']:
        if cv2 is not None:
            erodekernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
            eroded = cv2.erode(thres,erodekernel)
        else:
            erodekernel = disk(2, dtype=uint8)
            eroded = erosion(thres, erodekernel)

        if not set(('erode','all')).isdisjoint(P['makeplot']):
            ploterode(eroded,fn,P['odir'])

        print(erodekernel)
    else:
        eroded = thres
#%% dilation
    if cv2 is not None:
        dilatekernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        dilated = cv2.dilate(eroded,dilatekernel)
    else:
        dilatekernel = disk(2, dtype=uint8) #scikit-image
        dilated = dilation(eroded, dilatekernel)

    if not set(('dilate','all')).isdisjoint(P['makeplot']):
        plotdilate(dilated,data,maskdata,fn,P['odir'])


    print(dilatekernel)

    return dilated

def dolabel(data):

    if cv2 is None: #use scikit image
        cclbl,nlbl = label(data,neighbors=8,return_num=True)
        regions = regionprops(cclbl, data, True)
        centroids = empty((nlbl,2))
        for i,r in enumerate(regions):
            centroids[i,1],centroids[i,0] = r.centroid
        badind=[]
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
    return centroids,nlbl,badind

def dosum(data,centroids,nlbl,badind,fn,P):
    if P['verbose']:
        print('summing centroid radius {} pixels.'.format(P['centrad']))

    centRad = P['centrad']

    centroid_sum = empty(centroids.size)
    centroid_sum.fill(nan)

    for i,crc in enumerate(centroids):
        if i==badind:
            continue

        if cv2 is not None:
            circletmp = zeros_like(data) #slow!
            cv2.circle(circletmp,(crc[1],crc[0]),centRad,1,thickness=-1)
            csi = circletmp.astype(bool)
        else:
            csi = circle(crc[0], crc[1], radius=centRad, shape=data.shape) #scikit image

        centroid_sum[i] = data[csi].sum()

    if not set(('rawcentroid','all')).isdisjoint(P['makeplot']):
        plotcentroid(data,centroids,fn,P['odir'])

    return centroid_sum

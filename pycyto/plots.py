from numpy.ma import masked_where
from numpy import ones
from matplotlib.pyplot import figure,close,subplots
#from matplotlib.colors import LogNorm
#from matplotlib.ticker import LogFormatterMathtext

DPI=150 #resolution of saved plots

def writeplot(fg,ofn):
    if ofn:
        print('writing {}'.format(ofn))
        fg.savefig(str(ofn),dpi=DPI,bbox_inches='tight')
        close(fg)

def plotillum(im,Iang,invsq):
    test = ones(im.shape)

    out = test * Iang * invsq

    fg,axs = subplots(1,2,sharex=True,sharey=True)
    ax = axs[0]
    h=ax.pcolormesh(im,cmap='gray',vmax=out.max())
    ax.set_title('gaussian blur, poisson noise')
    fg.colorbar(h,ax=ax)
    ax.autoscale(True,tight=True)

    ax = axs[1]
    h = ax.imshow(out,'gray')
    fg.colorbar(h,ax=ax)
    ax.contour(invsq)
    ax.contour(Iang)
    ax.set_title('optical setup adjustment')

def plotraw(data,fn,odir):
    fg = figure()
    ax =fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='upper', interpolation='none')#, norm=LogNorm())
    fg.colorbar(hi)#,format=LogFormatterMathtext())
    ax.set_title('raw {} data:  {}'.format(data.dtype, fn))
    ax.autoscale(True)
    if odir:
        writeplot(fg,odir / (fn.name + '_raw.png'))

def plotthres(thres,data,maskdata,fn,odir):
    fg = figure()
    ax = fg.gca()
    ax.imshow(thres)
    ax.set_title('threshold binary result  {}'.format(fn))
    if odir:
       writeplot(fg,odir / (fn.name + '_thres.png'))

    maskthres = masked_where(thres,maskdata)
    fg = figure();
    ax = fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='upper', interpolation='none')#, norm=LogNorm())
    fg.colorbar(hi)#,format=LogFormatterMathtext())
    ax.imshow(maskthres,cmap = 'jet', interpolation = 'none')
    ax.set_title('thresholded data result  {}'.format(fn))
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    if odir:
       writeplot(fg,odir / (fn.name + '_thres_raw.png'))

def ploterode(eroded,fn,odir):
    fg = figure()
    ax = fg.gca()
    ax.imshow(eroded)
    ax.set_title('erosion binary result {}'.format(fn))
    if odir:
       writeplot(fg,odir / (fn.name + '_erode.png'))

def plotdilate(dilated,data,maskdata,fn,odir):
    fg = figure()
    ax = fg.gca()
    ax.imshow(dilated)
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.set_title('dilation binary result {}'.format(fn))
    if odir:
       writeplot(fg,odir / (fn.name + '_dilate.png'))

    maskdilate = masked_where(dilated,maskdata)
    fg = figure(); ax = fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='upper', interpolation='none')#, norm=LogNorm())
    fg.colorbar(hi)
    ax.imshow(maskdilate,cmap = 'jet', origin='upper',interpolation = 'none')
    ax.set_title('dilated data result  {}'.format(fn))
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    if odir:
        writeplot(fg,odir / (fn.name + '_dilate_raw.png'))

def plotcentroid(data,centroid_rc,fn,odir):
    assert data.ndim==2,'single image'
    assert centroid_rc.shape[1] == 2,'Ncell x 2   (row,column is second axis)'
    fg = figure()
    ax = fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='upper', interpolation='none')#, norm=LogNorm())
    hc = fg.colorbar(hi)
    hc.set_label('data numbers')
    ax.scatter(centroid_rc[:,0],centroid_rc[:,1], color='red')
    ax.set_title('centroids of {} connected regions: {}'.format(centroid_rc.shape[0],fn))
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.autoscale(True,'both',tight=True)
    if odir:
        writeplot(fg, odir / (fn.name + '_centroid.png'))

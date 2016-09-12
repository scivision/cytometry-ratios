from numpy.ma import masked_where
from matplotlib.pyplot import figure,close
#from matplotlib.colors import LogNorm
#from matplotlib.ticker import LogFormatterMathtext

def writeplot(fg,ofn,odir):
    if odir:
        print('writing {}'.format(ofn))
        fg.savefig(str(ofn),dpi=150,bbox_inches='tight')
        close(fg)

def plotraw(data,fn,odir):
    fg = figure()
    ax =fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
    fg.colorbar(hi)#,format=LogFormatterMathtext())
    ax.set_title('raw {} data:  {}'.format(data.dtype, fn))
    ax.autoscale(True)
    writeplot(fg,fn,odir / (fn.name + '_raw.png'))

def plotthres(thres,data,maskdata,fn,odir):
    fg = figure()
    ax = fg.gca()
    ax.imshow(thres)
    ax.set_title('threshold binary result  {}'.format(fn))
    writeplot(fg,fn,odir / (fn.name + '_thres.png'))

    maskthres = masked_where(thres,maskdata)
    fg = figure();
    ax = fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
    fg.colorbar(hi)#,format=LogFormatterMathtext())
    ax.imshow(maskthres,cmap = 'jet', interpolation = 'none')
    ax.set_title('thresholded data result  {}'.format(fn))
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    writeplot(fg,fn,odir / (fn.name + '_thres_raw.png'))

def ploterode(eroded,fn,odir):
    fg = figure()
    ax = fg.gca()
    ax.imshow(eroded)
    ax.set_title('erosion binary result {}'.format(fn))
    writeplot(fg,fn,odir / (fn.name + '_erode.png'))

def plotdilate(dilated,data,maskdata,dilatekernel,fn,odir):
    ax = figure().gca()
    ax.imshow(dilated)
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.set_title('dilation binary result {}'.format(fn))

    maskdilate = masked_where(dilated,maskdata)
    fg = figure(); ax = fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
    fg.colorbar(hi)
    ax.imshow(maskdilate,cmap = 'jet', interpolation = 'none')
    ax.set_title('dilated data result  {}'.format(fn))
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    print(dilatekernel)

def plotcentroid(data,centroid_rc,fn,odir):
    fg = figure()
    ax = fg.gca()
    hi = ax.imshow(data, cmap='gray', origin='lower', interpolation='none')#, norm=LogNorm())
    hc = fg.colorbar(hi)
    hc.set_label('data numbers')
    ax.plot(centroid_rc[:,1],centroid_rc[:,0],
            marker='.', linestyle='none',color='red',markersize=1)
    ax.set_title('centroids of {} connected regions  of {}'.format(centroid_rc.shape[0],fn))
    ax.set_xlabel('x-pixel')
    ax.set_ylabel('y-pixel')
    ax.autoscale(True,tight=True)

    writeplot(fg,fn,odir / (fn.name + '_centroid.png'))
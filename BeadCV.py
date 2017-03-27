#!/usr/bin/env python
"""
Alternative Background Subtraction
algorithm by Michael Hirsch
implemented by team 12 oscp
"""

from Imaging import Imaging, Camera
import numpy as np
from skimage.draw import circle
from skimage.measure import regionprops,label
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')


cam = Camera()
cam.configureGPIO()
cam.configureProperties()
imaging = Imaging(cam)
exposures = np.array([7000,3000])

TRIALS = 20


for trial in range(TRIALS):
    images = imaging.acquireImages(exposures=exposures) 

    print('trial #',trial)
    image = images[:,:,1]
    dx,dy = np.gradient(image)
    m = np.hypot(dx,dy)
    thres = m>(5*np.median(m))
                    
    cclbl,nlbl = label(thres,neighbors=8,return_num=True)
    regions = regionprops(cclbl, image, True)
    data = np.empty((len(regions),3))
    
    mean=[]
    sqmean=[]
    cent_next=[]
    
    for i,r in enumerate(regions):
        
        # grab centroids with appropriate bbox
        bbox_area = (r.bbox[2]-r.bbox[0])*(r.bbox[3]-r.bbox[1])
        data[i,:2] = r.centroid         
        data[i,2] = bbox_area
    data = data[(data[:,2] > 4) & (data[:,2] < 100)]
        
    if trial > 0:
        
        for j in range(data.shape[0]):
            #check if centroid is already located
            if np.min(np.hypot(data[j,0]-cent_last[:,0],data[j,1]-cent_last[:,1])) < 2:
                #find closest centroid in last image
                idx = (np.hypot(data[j,0]-cent_last[:,0],data[j,1]-cent_last[:,1])).argmin()
                cent_next.append((trial*cent_last[idx] + data[j,:2])/(trial+1))
                #calculate centroid-sum for current centroid in current image
                csi = circle(data[j,0], data[j,1], radius=3, shape=image.shape) 
                csum = image[csi].sum()
                #calculate mean and sqmean
                mean.append((trial*mean_last[idx] + csum)/(trial+1))
                sqmean.append((trial*sqmean_last[idx] + csum**2)/(trial+1))
    # initialization        
    else:
        cent_next = data
        for j in range(data.shape[0]):
            csi = circle(data[j,0], data[j,1], radius=3, shape=image.shape) 
            csum = image[csi].sum()
            mean.append(csum)
            sqmean.append(csum**2)
    
    mean_last = mean
    sqmean_last = sqmean
    cent_last = np.array(cent_next)[:,:2]
    
mean = np.array(mean_last)
sqmean = np.array(sqmean_last)

std = np.sqrt(sqmean-mean**2)

CV = 100*std/mean
good_ind = np.isfinite(CV)

plt.hist(CV[good_ind],50)
plt.title('CV measurement on beads')
plt.xlabel('CV')
plt.ylabel('number of bead centroids')
                    
cam.cleanUp()

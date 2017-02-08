# DATA COLLECTION
from __future__ import division
import matplotlib.pyplot as plt
import RPi.GPIO as gpio
from NormalizeData import *
from scipy.ndimage import gaussian_filter

if __name__ == '__main__':
    
    leds=[19,13]
    cam,lcd,encoder = init(leds)  
    initial_exposure=[2000,2000]
    trials = 200
    
    images = takePics(cam,leds,initial_exposure)
    smooth1 = gaussian_filter(images[0],4)
    smooth2 = gaussian_filter(images[1],4)
    max1 = np.max(smooth1)
    max2 = np.max(smooth2)
    y = np.argmax(np.max(smooth1,0))
    print(np.max(smooth1))
    print(y)
    exposures = normalize(images,initial_exposure[0],4)
    images2 = takePics(cam,leds,exposures)
    nmax1 = np.max(images2[0])
    nmax2 = np.max(images2[1])
    mean,meansq,std1,std2,mv1,mv2 = calcVar(cam,exposures,trials)
    print('Mean: {}, Mean Squared: {}, STD1: {}, STD2: {}'.format(mean,meansq,std1,std2))
    
    plt.figure()
    
    plt.subplot(231)
    plt.imshow(images[0],'gray',vmin=0,vmax=4095)
    plt.title('Initial Blue Image')
    plt.xlabel('X Pixel')
    plt.ylabel('Y Pixel')
    plt.subplot(232)
    plt.title('Intensity at Pixel ({},y)'.format(y))
    plt.xlabel('Y pixel')
    plt.ylabel('Image Intensity')
    plt.plot(images[0][:,y])
    plt.subplot(233)
    plt.plot(smooth1[:,y])
    plt.title('Smoothed Intensity, Max = {}'.format(max1))
    plt.xlabel('Y pixel')
    plt.ylabel('Image Intensity')    
  
    plt.subplot(234)
    plt.imshow(images[1],'gray',vmin=0,vmax=4095)
    plt.title('Initial UV Image')
    plt.xlabel('X Pixel')
    plt.ylabel('Y Pixel')
    plt.subplot(235)
    plt.title('Intensity at Pixel ({},y)'.format(y))
    plt.xlabel('Y pixel')
    plt.ylabel('Image Intensity')
    plt.plot(images[1][:,y])
    plt.subplot(236)
    plt.plot(smooth2[:,y])
    plt.title('Smoothed Intensity, Max = {}'.format(max2))
    plt.xlabel('Y pixel')
    plt.ylabel('Image Intensity')   
    
    
    plt.figure()
    plt.subplot(221)
    plt.title('Normalized Blue Image, Max = {}'.format(nmax1))
    plt.xlabel('X Pixel')
    plt.ylabel('Y Pixel')
    plt.imshow(images2[0],'gray',vmin=0,vmax=4095)
    plt.subplot(222)
    plt.xlabel('X Pixel')
    plt.ylabel('Y Pixel')
    plt.title('Smoothed Intensity at Pixel ({},y)'.format(y))
    plt.plot(images2[0][:,y])
    
    plt.subplot(223)
    plt.title('Normalized UV Image, Max = {}'.format(nmax2))
    plt.xlabel('Y pixel')
    plt.ylabel('Image Intensity')
    plt.imshow(images2[1],'gray',vmin=0,vmax=4095)
    plt.subplot(224)
    plt.title('Smoothed Intensity at Pixel ({},y)'.format(y))
    plt.xlabel('Y pixel')
    plt.ylabel('Image Intensity')
    plt.plot(images2[1][:,y])
    
    plt.figure()  
    plt.title('Max Intensity Value vs Trial')
    plt.ylabel('Max Intensity Value')
    plt.xlabel('Trial')
    plt.plot(mv1,'r',label='UV')
    plt.plot(mv2,'b',label='Blue')
    plt.legend()
    plt.ylim([0,4095])
    plt.show()
        
    cam.close()

  

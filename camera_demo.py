#!/usr/bin/env python
from __future__ import division, print_function
from pycyto import Path
from sys import stderr
import numpy as np
import matplotlib.pyplot as plt
import pypylon as pyl
import RPi.GPIO as gpio
from time import time
from datetime import datetime
try:
    import tifffile
except ImportError:
    tifffile = None
#
Nimg = 9
r,c = 1024,1280 # TODO read this from camera properties
ofn = Path('data').expanduser()

def testCamera(exposure_time,led_pin):
    cam.properties['ExposureTime'] = exposure_time
    tic = time()
    gpio.output(led_pin,gpio.HIGH)
    print(time()-tic)
    image = cam.grab_image()
    print(time()-tic)
    gpio.output(led_pin, gpio.LOW)
    print(time()-tic)
    return image

if __name__ == '__main__':
        
    led_pin = 26
    gpio.setmode(gpio.BCM)
    gpio.setup(led_pin, gpio.OUT)
    gpio.output(led_pin, gpio.LOW)
    
    available_cameras = pyl.factory.find_devices()
    cam = pyl.factory.create_device(available_cameras[0])
    cam.open()
    
    print('Camera Type')
    print(cam.device_info)
    
    for prop in cam.properties.keys():
        try:
            print(prop,end=': ')
            print(cam.properties[prop])
        except:
            print("Can't read", file=stderr)
       
    plt.figure()
    exposure_time=100
    cam.properties['ExposureAuto'] = 'Off'
    cam.properties['GainAuto'] = 'Off'
    cam.properties['Gain'] = 0
    ims = np.empty((Nimg,r,c),dtype='uint16')
    for i in range(Nimg):
        image = testCamera(exposure_time, led_pin)

        ax = plt.subplot(3,3,i+1)
        ax.set_title('exposure_time = {}'.format(exposure_time))
        ax.imshow(image, 'gray',
                  vmin=0, vmax=100)
        exposure_time += 100
        ims[i,...] = image
#%% write output to multipage TIFF at full fidelity
    if tifffile is not None:
        ofn = opath / '{}.tif'.format(datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        print('saving {} images to {}'.format(Nimg,ofn))
        tifffile.imsave(str(ofn), ims,
                        compress=6, # empirical, if taking too long to write, decrease number at expense of more disk space
                        photometric='minisblack', #not for color
            # these can be used for metadata
                        description=None,
                        extratags=None)
    
    cam.close()
    gpio.cleanup()

    plt.show()	
   
    
"""
It seems like the program holds up until the image is aquired, but this has only
been tested for software triggered image aquisition. We need to set the camera
properties to hardware trigger and see if the program will wait until the image
arrives.
"""

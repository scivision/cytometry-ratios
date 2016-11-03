import numpy as np
import  matplotlib.pyplot as plt
import pypylon as pyl
import RPi.GPIO as gpio
from time import time

def testCamera(exposure_time,led_pin):
    cam.properties['ExposureTime'] = exposure_time
    tic = time()
    gpio.output(led_pin,gpio.HIGH)
    print(time()-tic)
    image = cam.grab_image()
    print(time()-tic)
    gpio.output(led_pin,gpio.LOW)
    print(time()-tic)
    return image

if __name__ == '__main__':
        
    led_pin = 26
    gpio.setmode(gpio.BCM)
    gpio.setup(led_pin,gpio.OUT)
    gpio.output(led_pin,gpio.LOW)
    
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
            print("Can't read")
       
    plt.figure()
    exposure_time=100
    cam.properties['ExposureAuto'] = 'Off'
    cam.properties['GainAuto'] = 'Off'
    cam.properties['Gain'] = 0
    for i in range(9):
        image = testCamera(exposure_time,led_pin)

        plt.subplot(3,3,i+1)
        plt.title('exposure_time = {}'.format(exposure_time))
        plt.imshow(image,'gray',vmin=0,vmax=100)
        exposure_time += 100
    
    cam.close()
    plt.show()	
    gpio.cleanup()
    
"""
It seems like the program holds up until the image is aquired, but this has only
been tested for software triggered image aquisition. We need to set the camera
properties to hardware trigger and see if the program will wait until the image
arrives.
"""

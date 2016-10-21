#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 21:11:36 2016

@author: greg
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

number_of_cells = 50
led_angle = 30*np.pi/180 #degrees
distance_to_led = .1 #meters
slide_size = .02 #meters
pixels = 512
camera_depth=256

#set up the image with dots on it
image = np.zeros((pixels,pixels),dtype='uint8')
xpts = (np.random.rand(number_of_cells)*512).astype(int)
ypts = (np.random.rand(number_of_cells)*512).astype(int)
image[ypts,xpts] = int(.8*camera_depth)
poissonNoise = np.random.poisson(1,image.shape).astype('uint8')
image = gaussian_filter(image,1)

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
pixel_size = slide_size/pixels
X,Y = np.meshgrid(pixel_size*np.arange(-256,256),pixel_size*np.arange(-256,256))
distances = np.sqrt((distance_to_led*np.sin(led_angle))**2
                    +(distance_to_led*np.cos(led_angle)+X)**2
                    +Y**2)
inverse_square_mask = 1/distances**2
inverse_square_mask/=inverse_square_mask[256,256]
radiation_pattern = np.arccos((distance_to_led+X*np.cos(led_angle))/
                              np.sqrt(distance_to_led**2+Y**2+X**2+
                                     2*distance_to_led*X*np.cos(led_angle)))
angle_intensity_mask = 1-radiation_pattern**2/1.9

test = np.ones((pixels,pixels))
test_output = test*angle_intensity_mask*inverse_square_mask

#plot out a bunch of tests
plt.figure()
plt.imshow(test_output,'gray')
plt.colorbar()
plt.contour(inverse_square_mask)
plt.contour(angle_intensity_mask)
plt.title('optical setup adjustment')

image_w_optical = image*inverse_square_mask*angle_intensity_mask
plt.figure()
plt.pcolormesh(image_w_optical,cmap='gray')
plt.xlim((0,512))
plt.ylim((0,512))
plt.title('gaussian blur, poisson noise, optical adjustment')
plt.colorbar()

plt.figure()
plt.pcolormesh(image,cmap='gray',vmax=np.max(image_w_optical))
plt.xlim((0,512))
plt.ylim((0,512))
plt.title('gaussian blur, poisson noise')
plt.colorbar()
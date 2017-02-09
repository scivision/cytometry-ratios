"""
2/8/2017
script for calculating CV
and messing with bead pictures

"""

from Imaging import Imaging, Camera
import numpy as np
import matplotlib.pyplot as plt

cam = Camera()
cam.configureGPIO()
cam.configureProperties()

imaging = Imaging(cam)
imaging.loadNorm()

#imaging.init_exp = [10000,10000]

exposures = np.array([3000,3000])*imaging.ratios

imaging.acquireImages(exposures=exposures,mask=imaging.masks)


plt.figure()
plt.subplot(121)
plt.imshow(imaging.images[0],cmap='gray',vmin=0,vmax=4095)
plt.subplot(122)
plt.imshow(imaging.images[1],cmap='gray',vmin=0,vmax=4095)

"""
imaging.maskImage(masks)

plt.figure()
plt.subplot(121)
plt.imshow(imaging.images[0],vmin=0,vmax=4095)
plt.subplot(122)
plt.imshow(imaging.images[1],vmin=0,vmax=4095)
"""

cam.cleanUp()
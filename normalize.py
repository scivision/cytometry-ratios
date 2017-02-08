from __future__ import division
from numpy import (e,pi,meshgrid,arange,sin,sqrt,cos,arccos,exp,
                    zeros,max,random,argmax,argmin,ones_like,array)
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter


ledang = 20*pi/180 #degrees
ct = cos(ledang) #cosine of theta
leddist = .05 #meters
dc = leddist*ct #distance times cosine theta
slide_size = .005 #meters
Nxy = array((1280,960))
pixel_size = slide_size/Nxy
Fx,Fy = pixel_size*(1000*(random.rand(2)-.5))

# Slide Coordinates
X,Y = meshgrid(slide_size/Nxy[0] * arange(-Nxy[0]//2,Nxy[0]//2),
                  slide_size/Nxy[1] * arange(-Nxy[1]//2,Nxy[1]//2))

# Distance from LED to each pixel
distances = sqrt((leddist * sin(ledang))**2
                    +(leddist*cos(ledang)+X)**2
                    +Y**2)

# Normalized Inverse Square Mask
invsq = 1/distances**2
invsq /= invsq[Nxy[1]//2,Nxy[0]//2]

#Fx,Fy = .2,0

# Degrees off of LED direction vector
radiation_pattern = arccos((Fx*X+Fx*dc+X*dc+Fy*Y+leddist**2)/
                           sqrt((Fx**2+2*Fx*dc+Fy**2+leddist**2)*
                                (X**2+2*X*dc+Y**2+leddist**2)))

# LED fading away from center
Iang = 1 - radiation_pattern**2/1.9

# Image Formation
image = ones_like(X,'uint8')

# Center
cx = X[0,Nxy[0]//2]
cy = Y[Nxy[1]//2,0]

# Gaussian Viniette
Imax= 200
r = sqrt((X-cx)**2+(Y-cy)**2)
r0 = slide_size/5

camera = Imax*exp(-1*(r/r0)**3)
optical = invsq*Iang

image = camera*image

noise = random.poisson(5,image.shape)
image += noise
image = optical*image

plt.figure()
plt.pcolormesh(X,Y,image,cmap='gray',vmin=0,vmax=255)
plt.contour(X,Y,invsq)
plt.colorbar()
plt.plot(Fx,Fy,'wx')
plt.axis([-1*slide_size/2,slide_size/2,-1*slide_size/2,slide_size/2])

plt.figure()
plt.plot(Y[:,0],image[:,Nxy[0]//2])
plt.ylim([0,255])
plt.grid()
plt.figure()
plt.plot(X[0,:],image[Nxy[1]//2,:])
plt.ylim([0,255])
plt.grid()

# Spatially Normalize
C = Imax*ones_like(image)
smooth = gaussian_filter(image+noise,4)
reasonable = smooth>8
C[reasonable] = C[reasonable]/(smooth)[reasonable]
imagenorm = C*(image)
plt.figure()
plt.pcolormesh(X,Y,imagenorm,cmap='gray',vmax=255)
plt.colorbar()


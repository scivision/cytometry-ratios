import numpy as np
import  matplotlib.pyplot as plt
import pypylon as pyl

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
exposure_time=1000
cam.properties['ExposureAuto'] = 'Off'
for i in range(9):
    cam.properties['ExposureTime'] = exposure_time
    image = cam.grab_image()
    plt.subplot(3,3,i+1)
    plt.title('exposure_time = {}'.format(exposure_time))
    plt.imshow(image,'gray')
    exposure_time += 500

cam.close()
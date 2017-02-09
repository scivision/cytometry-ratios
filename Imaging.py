import RPi.GPIO as gpio
import numpy as np
from scipy.ndimage import gaussian_filter
import pypylon as pyl
import datetime
import matplotlib.pyplot as plt

"""

Camera

-Configures camera's properties
-Creates LED arrays
-Defines Exposures
-Sets GPIO's

"""

class Camera(object):

    def __init__(self):

        #Creates the device and LED's
        available_cameras = pyl.factory.find_devices()
        self.device = pyl.factory.create_device(available_cameras[0])
        self.leds = {26 : "UV", 19 : "B"} #  add "R"
        
    def configureGPIO(self):

        #Refer to the pins by Broadcom convention
        #Set up the leds output
        gpio.setmode(gpio.BCM)        

        for led in self.leds:
            gpio.setup(led,gpio.OUT)
            gpio.output(led,gpio.LOW)
            
        gpio.setup(6, gpio.IN, pull_up_down=gpio.PUD_UP)
       
    def configureProperties(self, exposure = 1500,
                            exposure_auto = 'Off',
                            gain_auto = 'Off',
                            overlap_mode = 'Off',
                            gain = 0,
                            pixel_format = 'Mono12',
                            shutter_mode = 'Global'):
        
        #Configure properties of the camera for sampling.
        #This removes some of the automatic settings/modes that could interfere with testing.
        self.device.open()        
        self.device.properties['ExposureTime'] = exposure
        self.device.properties['ExposureAuto'] = exposure_auto        
        self.device.properties['GainAuto'] = gain_auto
        self.device.properties['OverlapMode'] = overlap_mode
        self.device.properties['Gain'] = gain
        self.device.properties['PixelFormat'] = pixel_format
        self.device.properties['SensorShutterMode'] = shutter_mode

    def listProperties(self):

        #Print out the property list of the camera.
        for prop in self.device.properties.keys():
            
            try:
                print(prop,end=': ')
                print(self.device.properties[prop])

            except:
                print("Can't read")

    def cleanUp(self):
        gpio.cleanup()
        self.device.close()



"""

Imaging Functionality

-Acquire Picture
-Acquire N Pictures
-Mask an image
-Clear image list
-Normalize the exposures and spatial values

"""


class Imaging(Camera):


    def __init__(self, cam, patient=None):

        #Setup
        self.masks = []
        self.images = []        
        self.leds = {26 : "UV", 19 : "B"}
        self.cam = cam
        self.timestamps = {26 : [], 19 : []}
        self.patient = patient
        self.init_exp = [1500, 1500]
        
    def acquireImage(self, exposure, led):
        
        self.cam.device.properties['ExposureTime'] = exposure
        gpio.output(led, gpio.HIGH)
        image = self.cam.device.grab_image()
        gpio.output(led, gpio.LOW)

        return image

    def acquireImages(self, exposures=None, mask=False, document=False):
        if exposures == None:
            exposures = self.init_exp
        
        patient_file =  open("patient.txt", "a")

        led_index = 0
        for led in self.leds:
            self.images.append(self.acquireImage(exposures[led_index], led))
            if(document):
                self.document(led, patient_file)          
            led_index+=1
        if(mask.any()):
            self.maskImage(mask)
        patient_file.close()
        
        return self.images

    def document(self, led, patient_file):
        patient_file.write(self.patient)
        patient_file.write(datetime.datetime.now().strftime(" %A, %d. %B %Y %I:%M%p\n"))
        
        #Save to timestamps array instead
        #self.timestamps[led].append(self.patient)        
        #self.timestamps[led].append(datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))

    def maskImage(self, masks):
        self.images[0] = self.images[0]*masks[0]
        self.images[1] = self.images[1]*masks[1]

        return self.images

    def clearImages(self):
        self.images[:] = []


    #Normalization Functions

    def normalizeExposure(self, variance=10):
        normalized_exp = np.empty(2,float)
        max_intensities = np.empty(2,int)

        for i in range(len(self.images)):
            image = gaussian_filter(self.images[i],variance).astype(float)
            max_intensity = np.max(image)         
            max_intensities[i] = max_intensity

        normalized_exp[0] = 1.0
        normalized_exp[1] = max_intensities[0]/max_intensities[1]
        
#       DEBUG PRINT STATEMENTS
#        print("Max_Intensities[0] = ", max_intensities[0])
#        print("Max_Intensities[1] = ", max_intensities[1])
#        print("Normalized Exps = ", normalized_exp)
        return normalized_exp


    def normalizeSpatial(self):

        ratios = self.normalizeExposure()

        normal_exp = np.asarray(self.init_exp,int)*ratios
        
        #print("normal_exp ", normal_exp)

        #clear initial images        
        self.clearImages()
        
        normal_image = self.acquireImages(normal_exp)
        
        intensity_masks = np.ones_like(normal_image,dtype=float)  

        for i in range(len(normal_image)):
            corrected_image = gaussian_filter(normal_image[i],10).astype(float)
            max_intensity = np.max(corrected_image)
            intensity_masks[i] = max_intensity/corrected_image
            
        return intensity_masks       
        
        
    def fullyNormalize(self):
        
        self.acquireImages()
        ratios = self.normalizeExposure()
        masks = self.normalizeSpatial()
        
        np.save('masks',masks)
        np.save('ratios',ratios)
        
    def loadNorm(self):
        
        self.ratios = np.load('ratios.npy')
        self.masks = np.load('masks.npy')
    
    

#Old method from before that may still be useful   
 
 
        #Calculates the mean, rms, standard deviations   
    def runTrials(self, trials=10):
        
        #Pass number of images to take
        TRIALS = trials
                
        #Max value arrays to store the max value of each image caputre
        maxvals = np.empty(TRIALS)
        maxvals2 = np.empty(TRIALS)
        
        #Acquire inital images and normalize expousre
        self.acquireImages()
        ratios = self.normalizeExposure()

        normal_exp = np.asarray(self.init_exp,int)*ratios
        
        print("Normalized Exposure for trials " , normal_exp)
        
        #Acquire TRIALS number of images 
        for i in range(TRIALS):
            normal_image = self.acquireImages(normal_exp)
            maxvals[i] = np.max(normal_image[0])
            maxvals2[i] = np.max(normal_image[1])

        
        mean = np.mean(maxvals-maxvals2)
        rms = np.sqrt(np.mean((maxvals-maxvals2)**2))
        std1 = np.std(maxvals)
        std2 = np.std(maxvals2)
        
        print("Mav values {}, {}", maxvals, maxvals2)
        print('Mean: {}, Mean Squared: {}, STD1: {}, STD2: {}'.format(mean,rms,std1,std2))
        plt.figure()
        plt.plot(maxvals,'r',label='UV')
        plt.plot(maxvals2,'b',label='Blue')
        plt.legend()
        plt.ylim([0,4096])
        plt.show() 
        
        return mean,rms,std1,std2,maxvals,maxvals2
      
      
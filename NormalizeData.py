from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import pypylon as pyl
import RPi.GPIO as gpio
from scipy.ndimage import gaussian_filter
import Adafruit_CharLCD as LCD

from time import time,sleep
import gaugette.rotary_encoder


def acquire(cam,exposure_time,led_pin):
    cam.properties['ExposureTime'] = exposure_time
    gpio.output(led_pin,gpio.HIGH)
    image = cam.grab_image()
    gpio.output(led_pin,gpio.LOW)
    return image
    
def listProperties(cam):
    for prop in cam.properties.keys():
        try:
            print(prop,end=': ')
            print(cam.properties[prop])
        except:
                print("Can't read")


def end():
    gpio.cleanup()
    cam.close()
    
def calcVar(cam,exposures,trials):
    
    TRIALS = trials
    led = [19, 13]
    
    maxvals = np.empty(TRIALS)
    maxvals2 = np.empty(TRIALS)

    for i in range(TRIALS):
        images = takePics(cam,led,exposures)
        maxvals[i] = np.max(images[0])
        maxvals2[i] = np.max(images[1])
        lcd.set_cursor(1,1)
        lcd.message(str(i))
    
    mean = np.mean(maxvals-maxvals2)
    rms = np.sqrt(np.mean((maxvals-maxvals2)**2))
    std1 = np.std(maxvals)
    std2 = np.std(maxvals2)
    return mean,rms,std1,std2,maxvals,maxvals2
  
  
def init(leds):
            
    #SETUP LEDS
    #13 Blue, 19 = UV, 26 = Red 
    #leds = [26,19,13]
    gpio.setmode(gpio.BCM)
    
    for i in leds:
        gpio.setup(i,gpio.OUT)
        gpio.output(i,gpio.LOW)
    
    #SETUP START BUTTON
    gpio.setup(6, gpio.IN, pull_up_down=gpio.PUD_UP)
    
    
    #SETUP CAMERA
    available_cameras = pyl.factory.find_devices()
    cam = pyl.factory.create_device(available_cameras[0])
    cam.open()
    cam.properties['ExposureAuto'] = 'Off'
    cam.properties['GainAuto'] = 'Off'
    cam.properties['OverlapMode'] = 'Off'
    cam.properties['Gain'] = 0
    cam.properties['PixelFormat'] = 'Mono12'
    
    # Raspberry Pi pin configuration:
    lcd_rs        = 27
    lcd_en        = 22
    lcd_d4        = 25
    lcd_d5        = 24
    lcd_d6        = 23
    lcd_d7        = 18
    lcd_backlight = 4
    
    
    #Rows and columns
    lcd_columns = 16
    lcd_rows    = 2
    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                               lcd_columns, lcd_rows, lcd_backlight)
                               
    A_PIN  = 7
    B_PIN  = 9

    encoder = gaugette.rotary_encoder.RotaryEncoder(A_PIN, B_PIN)

    return cam,lcd,encoder


def takePics(cam,leds,exp=[1500,1500]):
    images = []
    for i in leds:
        images.append(acquire(cam,exp[leds.index(i)],i))  
    return images
    
    
def normalize(images,input_exposure,variance=10):
    exposures=np.empty(2,int)
    intensities=np.empty(2,int)
    for i in range(len(images)):
        image = gaussian_filter(images[i],variance)
        intensity = np.max(image)
        intensities[i] = intensity
        
    exposures[0] = input_exposure
    exposures[1] = int(input_exposure*intensities[0]/intensities[1])
        
    return exposures
    
# Raspberry Pi pin configuration:
lcd_rs        = 27
lcd_en        = 22
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 18
lcd_backlight = 4


#Rows and columns
lcd_columns = 16
lcd_rows    = 2
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)
    

    
    
if __name__ == '__main__':
    
    leds=[19,13]
    cam = init(leds)
    initial_exposure=[1500,1500]
    trials = 100
    

    images = takePics(cam,leds,initial_exposure)
    exposures = normalize(images,initial_exposure[0],4)
    mean,meansq,std1,std2,mv1,mv2 = calcVar(cam,exposures,trials)
    print('Mean: {}, Mean Squared: {}, STD1: {}, STD2: {}'.format(mean,meansq,std1,std2))
    plt.figure()
    plt.plot(mv1,'r',label='UV')
    plt.plot(mv2,'b',label='Blue')
    plt.legend()
    plt.ylim([0,4095])
        
    
  

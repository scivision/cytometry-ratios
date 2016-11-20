# Deliverables Testing

import matplotlib.pyplot as plt
import RPi.GPIO as gpio
from NormalizeData import *

from time import sleep

def picProgram(cam,lcd,encoder):
    #Display start sequence
    exposure=[1500,1500]
    lcd.clear()    
    lcd.message('Button to Start\nExposure:{}'.format(exposure[0]))
    sleep(1)
    encoder_value = 0
    last_value = 0

    while True:
        
        encoder_value -= encoder.get_delta()
        if(abs(encoder_value-last_value)==4):
            exposure[0] += 100*int((encoder_value-last_value)/4)
            if(exposure[0]<10): exposure[0]=100
            exposure[1] = exposure[0]
            last_value = encoder_value
            lcd.set_cursor(9,1)
            lcd.message('       ')
            lcd.set_cursor(9,1)
            lcd.message(str(exposure[0]))
        
        if gpio.input(6) == False:
        
            lcd.clear()        
            lcd.message('Capturing..')
            images = takePics(cam,leds,exposure)
            sleep(1)                      

            break        

    lcd.clear()
    lcd.message('Capture Complete')
    sleep(1)
            
    plt.figure()
    plt.subplot(121)
    plt.imshow(images[0],'gray',vmin=0,vmax=4095)
    plt.title('Blue')
    plt.subplot(122)
    plt.imshow(images[1],'gray',vmin=0,vmax=4095)
    plt.title('UV')
    plt.ion()
    plt.pause(.001)
    plt.show()
    

def normProgram(cam,lcd,encoder):
    
    #Display start sequence
    initial_exposure=[1500,1500]
    trials = 100
    lcd.clear()    
    lcd.message('Button to Start\nTrials:{}'.format(trials))
    sleep(1)
    encoder_value = 0
    last_value = 0

    while True:
        
        encoder_value -= encoder.get_delta()
        if(abs(encoder_value-last_value)==4):
            trials += 10*int((encoder_value-last_value)/4)
            if(trials<10): trials=10
            last_value = encoder_value
            lcd.set_cursor(7,1)
            lcd.message('       ')
            lcd.set_cursor(7,1)
            lcd.message(str(trials))
        
        if gpio.input(6) == False:
        
                
            lcd.clear()        
            lcd.message('Capturing..')
            images = takePics(cam,leds,initial_exposure)
            sleep(1)
            
            lcd.clear()
            lcd.message('Normalizing')
            exposures = normalize(images,initial_exposure[0],4)
            sleep(1)
            
            lcd.clear() 
            lcd.message('Testing:')
            mean,rms,std1,std2,mv1,mv2 = calcVar(cam,exposures,trials)
                    

            break        

    
    lcd.clear()
    lcd.message('Testing Complete')
    sleep(2)
    
    lcd.clear()
    lcd.message('Turn dial for\nresults')
    
    results = 'Mean Error:\n{:.2f} = {:.2f}%,RMS Error:\n{:.2f},STD1:\n{:.2f},STD2:\n{:.2f}'.format(mean,100*abs(mean)/4096,rms,std1,std2)
    results = results.split(',')
    
    while True:
        
        if gpio.input(6) == False:
            break
        encoder_value -= encoder.get_delta()
        if(abs(encoder_value-last_value)==4):
            last_value = encoder_value
            lcd.clear()
            lcd.message(results[int(encoder_value/4)%4])
            
    plt.figure()
    plt.plot(mv1)
    plt.plot(mv2)
    plt.ylim([0,4095])
    plt.xlabel('Trial')
    plt.ylabel('Maximum Intensity')
    plt.ion()
    plt.pause(.001)
    plt.show()

    
def deliverables(cam,lcd,encoder):
    end=False
    lcd.clear()
    lcd.message('Select Program')
    programs=['Normalization','Camera Functions','Quit']    
    program_to_run=0
    lcd.set_cursor(0,1)
    lcd.message(programs[program_to_run])
    last_value=0
    encoder_value = 0
    while True:

        if gpio.input(6) == False:
            if(program_to_run==2):
                end=True
                break
            if(program_to_run==0):
                normProgram(cam,lcd,encoder)
                end = deliverables(cam,lcd,encoder)
                if(end): break
                sleep(1)
            elif(program_to_run==1):
                picProgram(cam,lcd,encoder)
                end = deliverables(cam,lcd,encoder)
                if(end): break
                sleep(1)

        encoder_value -= encoder.get_delta()
        if(abs(encoder_value-last_value)==4):
            last_value = encoder_value
            lcd.set_cursor(0,1)
            lcd.message('                ')
            lcd.set_cursor(0,1)
            program_to_run = int(encoder_value/4)%3
            lcd.message(programs[program_to_run])
            
    return end
 
    

if __name__ == '__main__':
    print('RUN FROM COMMAND LINE WITH "sudo python3 DeliverablesTesting.py"')
    
    leds=[19,13]
    cam,lcd,encoder = init(leds)    
    
    deliverables(cam,lcd,encoder)
                
    lcd.clear()
    lcd.message('goodbye')
    sleep(1)
    lcd.clear()
    
    cam.close()

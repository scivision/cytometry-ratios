import gaugette.rotary_encoder
import Adafruit_CharLCD as LCD
import RPi.GPIO as gpio

from time import sleep

"""
LCD Functionality

-Define pins
-Creates the lcd object

"""


class Lcd:


    def __init__(self):
     
        #Pin Configurations on the Raspberry Pi
        lcd_rs = 27
        lcd_en = 22
        lcd_d4 = 25
        lcd_d5 = 24
        lcd_d6 = 23
        lcd_d7 = 18
        lcd_backlight = 4       
        lcd_columns = 16
        lcd_rows  = 2
            
        #Pins for Encoder           
        a_pin = 7
        b_pin = 9
        
        #Global LCD state-variable
        STATE = 0

        #Setup the LCD screen and encoder
        self.board = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                                   lcd_columns, lcd_rows, lcd_backlight)

        self.encoder = gaugette.rotary_encoder.RotaryEncoder(a_pin, b_pin)
        self.board.clear()
        self.board.message('PC Mode')

        gpio.setmode(gpio.BCM)
        gpio.setup(6, gpio.IN, pull_up_down=gpio.PUD_UP)
    
    def boxMode(self):
        self.board.clear()
        self.board.message('Select Program')
        
        programs=['Normalization','Camera Functions','Quit']    
        program_to_run=0
        self.board.set_cursor(0,1)
        self.board.message(programs[program_to_run])
        last_value=0
        encoder_value = 0
        sleep(1)

#      #TO DO: Actually implement this. easiest done with returning values to main
#        while True:
#            
#            if gpio.input(6) == False:
#                if(program_to_run==2):
#                    break
#                if(program_to_run==0):
##                    normProgram(cam,lcd,encoder)
##                    end = deliverables(cam,lcd,encoder)
##                    if(end): break
#                    sleep(1)
#                    break
#                elif(program_to_run==1):
##                    picProgram(cam,lcd,encoder)
##                    end = deliverables(cam,lcd,encoder)
##                    if(end): break
#                    sleep(1)
#                    break
#
#            encoder_value -= self.encoder.get_delta()
#            if(abs(encoder_value-last_value)==4):
#                last_value = encoder_value
#                self.board.set_cursor(0,1)
#                self.board.message('                ')
#                self.board.set_cursor(0,1)
#                program_to_run = int(encoder_value/4)%3
#                self.board.message(programs[program_to_run])     
#

    #Need to add functionality for common displays (i.e "Home screen" that is displaying properties)
    #Possible use case-statements and have a state-machine type of deal

"""
Ex: def scrollState(state):
        if state==1:
            LCD display 'Processing'
        elif state == 2:
            LCD display 'Results'
            
        .
        .
        .
        

"""

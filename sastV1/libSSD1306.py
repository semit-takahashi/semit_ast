#!/usr/bin/python3
#
# logging
import logging 

# Adafruit SSD1306 Library
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

import sys
import subprocess
from libMachineInfo import getIPAddr, getMachine_Temp, getMachine_Volt, getHostname, getSSID

ARW = ['↗','→','↘']
ABC = ['ⓐ','ⓑ','ⓒ']

class OLED:
    disp = None
    image = None
    draw = None
    width = 0
    height = 0
    padding = 0
    top = 0
    bottom = 0
    X = 0
    Y = 0
    size = 16
    font = None
    fontS = None

    d = {}

    def __init__(self):
        #logging.debug('OLED : __init__')

        RST = None
        try:
            # create SSD1306
            self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3c)
        except Exception as e:
            logging.warning("Error SSD1306 init : ".format(e))
            self.disp = None
            return 

        # init library
        self.disp.begin()
        self.disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        self.padding = -2
        self.top = self.padding
        self.bottom = self.height-self.padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.x = 0

        # Load default font.
        #self.fontS = ImageFont.load_default()
        #self.fontS = ImageFont.truetype("Minecraft.ttf",11)
        #self.fontS = ImageFont.truetype("Minecraftia-Regular.ttf",10)
        self.fontS = ImageFont.truetype("/home/pi/font/DotGothic16-Regular.ttf",11)
        self.font = ImageFont.truetype("fonts-japanese-gothic.ttf", 16)
         

    ''' 送信データのコピー作成 '''
    def copyDATA(self, dt ):
        # format
        if( 'd1' not in dt ):
            dt['d1'] = "----"
        if( 'd2' not in dt ):
            dt['d2'] = "----"
        if( 'd3' not in dt ):
            dt['d3'] = "----"
        if( 'd4' not in dt ):
            dt['d4'] = "----"
        if( 'd5' not in dt ):
            dt['d5'] = "----"
        if( 'd6' not in dt ):
            dt['d6'] = "----"
        if( 'd7' not in dt ):
            dt['d7'] = "----"
        if( 'd8' not in dt ):
            dt['d8'] = "----"
        import copy
        return copy.copy(dt)

    ''' 画面クリア '''
    def clear(self):
        if( self.disp == None ):
            return
        self.disp.clear()
        self.disp.display()
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

    def text(self,x, y, mess , ANSI = False ):
        if( self.disp == None ):
            return
        if( ANSI == True ):
            self.draw.text((x,y), mess, font=self.fontS, fill=255)
        else:
            self.draw.text((x,y), mess, font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()

    def showPI(self):
        logging.debug('OLED : showPI')
        if( self.disp == None ):
            return

        self.clear()

        cmd = "/bin/df -h | /usr/bin/awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True ).decode()

        IP = getIPAddr()
        Temp = getMachine_Temp()
        Volt = getMachine_Volt()
        SSID = getSSID()
     
        # Write two lines of text.
        self.draw.text((0,  0), f"{IP}",font=self.fontS, fill=255)
        self.draw.text((0, 10), f"{SSID}", font=self.fontS, fill=255)
        self.draw.text((0, 25), f"Temp:{Temp:.1f}C", font=self.fontS, fill=255)
        self.draw.text((0, 35), f"Volt:{Volt:.1f}V", font=self.fontS, fill=255)
        self.draw.text((0, 45), f"{Disk}" ,font=self.fontS, fill=255)
        self.disp.image(self.image)
        self.disp.display()

    
    def showStatus( self, dt, sens = 2, pre = None, send = None):
        logging.debug("OLED : showSatus( sens={} )".format(sens))
        if( self.disp == None ):
            return

        # -- データコピーと整形
        self.d = copyDATA(dt)
        d = self.d

        #時刻を取り出し
        time = d['created'].split(' ')
        time = time[1]
        time = time[:5]

        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
        self.draw.text((0, 0 ),      f"ⓐ{d['d1']}C",font=self.font, fill=255)
        if( sens >= 2 ):
            self.draw.text((0, 16),  f"ⓑ{d['d3']}C",font=self.font, fill=255)
        if( sens == 3 ):
            self.draw.text((0, 32),  f"ⓒ{d['d5']}",font=self.font, fill=255)
        if( dt['d8'] != '----' ):
            self.draw.text((8*8, 16),f"{d['d8']}Pa",font=self.font, fill=255)

        self.draw.text((8*9,0),      f"{d['d7']}C",font=self.font, fill=255)
        self.draw.text((0,48),f"{time}",font=self.font, fill=255)

        if( send != None ):
            if( net1 == True ):
                self.draw.text((6,48),"×")
            else:
                self.draw.text((6,48)," ")

#        if( net2 != None ):
#            if( net1 == True ):
#                self.draw.text((6,48),"×")
#            else:
#                self.draw.text((6,48)," ")
#
#        self.disp.image(self.image)
#        self.disp.display()


if __name__ == '__main__':
    o = OLED()
    o.showPI()




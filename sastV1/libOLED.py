#!/usr/bin/python3
#
# logging
import logging 

# Adafruit SSD1306 Library
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

import copy
import sys
import subprocess
from libMachineInfo import getIPAddr, getMachine_Temp, getMachine_Volt, getHostname, getSSID

ARW = ['↗','▶','↘',' ']
ABC = ['ⓐ','ⓑ','ⓒ']
SNS = ['d1','d3','d5']

class OLED:
    ## -- SSD1306 data
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

    #-- latest senseor data
    d_prev = {}
    d = {}
    d_rate = {}
    SENS = 1

    #-- latest sensor STSTUS( BATT & RSSI ) 
    SSTAT = [None, None, None]

    def __init__(self, sens = 1):
        #logging.debug('OLED : __init__')

        self.SENS = sens

        RST = None
        try:
            # create SSD1306
            self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3c)
        except Exception as e:
            logging.warning("Error SSD1306 init : ".format(e))
            self.disp = None
            return 

        self.disp.begin()
        self.disp.display()
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

        # Draw some shapes.
        self.padding = -2
        self.top = self.padding
        self.bottom = self.height-self.padding
        self.x = 0

        # Load default font.
        #self.fontS = ImageFont.load_default()
        #self.fontS = ImageFont.truetype("Minecraft.ttf",11)
        #self.fontS = ImageFont.truetype("Minecraftia-Regular.ttf",10)
        self.fontS = ImageFont.truetype("/home/pi/font/DotGothic16-Regular.ttf",11)
        self.font = ImageFont.truetype("fonts-japanese-gothic.ttf", 16)
         

    def clear(self):
        if( self.disp == None ):
            return
        self.disp.clear()
        self.disp.display()
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

    ''' 送信データのコピーを作成してデータフォーマット '''
    def copyDATA(self, dt ):
        #logging.debug(f"copyDATA {dt}")
        if( 'd1' not in dt or dt['d1'] is None):
            dt['d1'] = "----"
        if( 'd2' not in dt or dt['d2'] is None):
            dt['d2'] = "----"
        if( 'd3' not in dt or dt['d3'] is None):
            dt['d3'] = "----"
        if( 'd4' not in dt or dt['d4'] is None):
            dt['d4'] = "----"
        if( 'd5' not in dt or dt['d5'] is None):
            dt['d5'] = "----"
        if( 'd6' not in dt or dt['d6'] is None):
            dt['d6'] = "----"
        if( 'd7' not in dt or dt['d7'] is None):
            dt['d7'] = "----"
        if( 'd8' not in dt or dt['d8'] is None):
            dt['d8'] = "----"

        import copy
        #logging.debug(f"->out {dt}")
        return copy.copy(dt)


    ''' 過去（prv）と現在（now）のデータを比較して矢印マークを返す 0.5以上'''
    def getRateMark( self, prv, now ):
        ### -変化量が無い場合 
        if( prv == '----' or now == '----' ):
            return ARW[3]

        rate = prv - now
        logging.debug(f"[getRateMark] prv{prv} now{now} rate={rate} ")
        if( rate < -0.5 ):
            ## 変化 -0.5以上→ 温度高く 
            return ARW[0]
        elif( rate > 0.5 ):
            ## 変化  0.5以上→温度低く
            return ARW[2]
        else:
            ## 変化無し(-0.5 ~ 0.5の範囲内)
            return ARW[1]
        

    ''' 表示データを作成し過去データと比較 '''
    def makeDATA( self, dt):
        logging.debug(f"[makeDATA] {dt}, {self.d_prev} ") 
        ## 現在のデータを過去データとしてコピー 
        if( len(self.d_prev) == 0 ):
            # -- 初回はデータ無いのでリターン
            for s in SNS:
                self.d_rate[s] = ARW[3]
            self.d = self.copyDATA( dt )
            self.d_prev = copy.copy( self.d )
            return False

        self.d_prev = copy.copy( self.d )

        ## 新しいデータを作成
        self.d = self.copyDATA( dt )

        for s in SNS:
            if( dt[s] != None ):
                self.d_rate[s]=self.getRateMark( self.d_prev[s], self.d[s] )
                logging.debug(f">> key={s}  {self.d_prev[s]}->{self.d[s]} {self.d_rate[s]}") 

    def locate(self,x,y):
        if( self.disp == None ):
            return
        self.X = x
        self.Y = self.size * y

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

        cmd = "/bin/hostname -I | /usr/bin/cut -d\' \' -f1"
        IP = getIPAddr()
        if( IP == '0.0.0.0' ):
            IP = "[No IP Address!]"
        elif( IP.startswith('169.254') ):
            IP = f"inPriv! {IP}"

        cmd = "/bin/df -h | /usr/bin/awk '$NF==\"/\"{printf \"disk %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True ).decode()

        Temp = getMachine_Temp()
        Volt = getMachine_Volt()

        SSID = getSSID()
     
        ## --- display
        self.draw.rectangle(( 0, 0,self.width,self.height), outline=0, fill=0)
        self.draw.text((0,  0), f"{IP}",font=self.font, fill=255)
        self.draw.text((0, 16), f" {SSID}", font=self.fontS, fill=255)
        self.draw.text((0, 32), f"name {getHostname()}", font=self.font, fill=255)
        self.draw.text((0, 49), f"{Disk}",  font=self.font, fill=255)
        #self.draw.text((0, 38), f"Temp:{Temp:.1f}C Volt:{Volt:.1f}V", font=self.fontS, fill=255)
        self.disp.image(self.image)
        self.disp.display()

    def updateStatus( self, dt, net1=None ,net2=None):  
        logging.debug("[OLED] updateSatus()")
        if( net1 != None ):
            dt['net1'] = net1
        if( net2 != None ):
            dt['net2'] = net2
        self.makeDATA( dt )

    def showStatus( self ):
        logging.debug(f"[OLED] showSatus()")

        d = self.d
        m = self.d_rate

        #時刻を取り出し
        time = d['created'].split(' ')
        date = time[0]
        time = time[1]
        time = time[:5]

        #データ整形
        dt = [0]*3
        dm = [0]*3
        dn = [0]*2

        dt[0] = "----" if type(d['d1']) is not float else f"{d['d1']:>4.1f}"
        dt[1] = "----" if type(d['d3']) is not float else f"{d['d3']:>4.1f}"
        dt[2] = "----" if type(d['d5']) is not float else f"{d['d5']:>4.1f}"
        dn[0] = "o" if d['net1'] == 0 else "x"
        dn[1] = "o" if d['net2'] == 0 else "x"

        ## --- 表示 温度表示
        self.draw.rectangle(( 0, 0,self.width,self.height), outline=0, fill=0)
        self.draw.rectangle((60,-1,128,38), outline=1, fill=0)
        self.draw.text((0, 0 ),      f"ⓐ{dt[0]}{m['d1']}",font=self.font, fill=255)
        if( self.SENS >= 2 ):
            self.draw.text((0, 16),  f"ⓑ{dt[1]}{m['d3']}",font=self.font, fill=255)
        if( self.SENS == 3 ):
            self.draw.text((0, 32),  f"ⓒ{dt[2]}{m['d5']}",font=self.font, fill=255)
        if( d['d8'] != '----' ):
            self.draw.text((8*8, 16),f"{d['d8']}hP",font=self.font, fill=255)

        self.draw.text((8*8,0),      f"  {d['d7']}℃",font=self.font, fill=255)
        self.draw.text((0,49),f"{date} {time}",font=self.font, fill=255)

        self.draw.text((14*8,35),dn[0], font=self.fontS, fill=255)
        self.draw.text((15*8,35),dn[1], font=self.fontS, fill=255)

        self.disp.image(self.image)
        self.disp.display()

    def updateStatus2(self, batts):
        self.SSTAT = copy.copy( batts )

    def showStatus2(self):
        logging.debug(f"[OLED] showSatus2()")

        d = self.d
        m = self.d_rate

        #時刻取り出し
        time = d['created'].split(' ')
        date = time[0]
        time = time[1]
        time = time[:5]

        #データ作成
        dh = [0] * 3
        dh[0] = "----" if type(d['d2']) is not float else f"{d['d2']:>4.1f}"
        dh[1] = "----" if type(d['d4']) is not float else f"{d['d4']:>4.1f}"
        dh[2] = "----" if type(d['d6']) is not float else f"{d['d6']:>4.1f}"

        db = [0] * 3
        dr = [0] * 3
        num = 0
        for B in self.SSTAT:
            if( B is not None ):
                db[num] = "----" if type(B[0]) is not int else f"{B[0]:3d}%"
                dr[num] = "----" if type(B[1]) is not int else f"{B[1]:4d}"
            else:
                db[num] = "----"
                dr[num] = "----"
            num += 1

        ## -- 表示 バッテリー
        self.draw.rectangle(( 0, 0,self.width,self.height), outline=0, fill=0)
        self.draw.text((0, 0 ),      f"ⓐ[{db[0]}] {dr[0]}dBm",font=self.font, fill=255)
        if( self.SENS >= 2 ):
            self.draw.text((0, 16),  f"ⓑ[{db[1]}] {dr[1]}dBm",font=self.font, fill=255)
        if( self.SENS == 3 ):
            self.draw.text((0, 32),  f"ⓒ[{db[2]}] {dr[2]}dBm",font=self.font, fill=255)
        self.draw.text((0,49),f"{dh[0]}% {dh[1]}% {dh[2]}%",font=self.font, fill=255)
        #self.draw.text((0,49),f"{date} {time}",font=self.font, fill=255)

        self.disp.image(self.image)
        self.disp.display()


''' MAIN '''
if __name__ == '__main__':
    import time
    logging.basicConfig(level=logging.INFO)
    o = OLED(sens=3)

    #time.sleep(1)
    data = {} 
    data['created'] = "2021-03-04 12:34:56"
    data['d1'] = 10.0
    data['d3'] = 10.0
    data['d5'] = 10.0
    data['d7'] = 42.3
    data['d8'] = 1234.6
    data['net1'] = 1
    data['net1'] = 1
    o.updateStatus( dt=data, net1=True, net2=True)
    o.showStatus()

    time.sleep(1)
    data = {} 
    data['created'] = "2021-03-04 12:34:56"
    data['d1'] = 10.2
    data['d3'] = 13.5
    data['d5'] = 04.6
    data['d7'] = 42.3
    data['d8'] = 1234.6
    data['net1'] = 1
    data['net1'] = 1
    o.updateStatus( dt=data, net1=True, net2=True)
    o.showStatus()

    o.clear()

    o.showStatus()


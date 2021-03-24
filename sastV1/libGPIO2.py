#!/usr/bin/python3
import logging
import RPi.GPIO as GPIO
import time
import threading
from enum import Enum

#--- GPIO PIN Setting
SENS_LED = [
    [ 21 , 26 ],   # NO1[ Green, Red ]
    [ 20 , 19 ],   # NO2[ Green, Red ]
    [ 16 , 13 ]    # NO3[ Green, Red )
]
STAT_LED = 6
SW_RHT = 4
SW_LFT = 12

BLK_1 = 0.3
# --- LED status Enum
class LSTAT(Enum):
    OFF    =0, 
    GR     =1, 
    RD     =2, 
    YW     =3, 
    GR_BLK =4, 
    RD_BLK =5

# --- IO Class
class IO:
    LED_STAT  = [LSTAT.OFF,LSTAT.OFF,LSTAT.OFF]
    LED_BLINK = [False,False,False]
    LED_THRED = [None,None,None]

    def __init__(self, rsw_callback=None, lsw_callback=None):
        logging.debug("GPIO init")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        ## 出力LEDの設定
        for pin in SENS_LED:
            GPIO.setup(pin, GPIO.OUT)
        GPIO.setup(STAT_LED, GPIO.OUT)

        # RIGHT SW
        if( rsw_callback != None ):
            #logging.debug("GPIO RIGHT SW callback={}".format(rsw_callback))
            GPIO.setup(SW_RHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(SW_RHT, GPIO.RISING, callback=rsw_callback, bouncetime=300)

        # LEFT SW
        if( lsw_callback != None):
            #logging.debug("GPIO LEFT SW callback={}".format(lsw_callback))
            GPIO.setup(SW_LFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(SW_LFT, GPIO.RISING, callback=lsw_callback, bouncetime=300)

    def BLINK( self, num, col):
        on = True
        while( IO.LED_BLINK[num-1] ):
            if( on ):
                GPIO.output(SENS_LED[num-1][col],GPIO.HIGH)
                #logging.debug(f"SENS{num} col={col} HIGH {threading.get_ident()}")
                time.sleep(BLK_1)
            else:
                GPIO.output(SENS_LED[num-1][col],GPIO.LOW)
                #logging.debug(f"SENS{num} col={col} LOW {threading.get_ident()}")
                time.sleep(BLK_1)
            on = not on
        GPIO.output(SENS_LED[num-1][col],GPIO.LOW)

    def close(self):
        logging.debug("GPIO Cleanup")
        GPIO.cleanup()

    def LED(self, num , stat ):
        if  ( stat == LSTAT.OFF ):
          if( IO.LED_BLINK[num-1] is True ):
            IO.LED_BLINK[num-1] = False
            IO.LED_THRED[num-1].join()
          GPIO.output(SENS_LED[num-1][0],GPIO.LOW)
          GPIO.output(SENS_LED[num-1][1],GPIO.LOW)

        elif( stat == LSTAT.GR ):
          GPIO.output(SENS_LED[num-1][0],GPIO.HIGH)
          GPIO.output(SENS_LED[num-1][1],GPIO.LOW)

        elif( stat == LSTAT.RD ):
          GPIO.output(SENS_LED[num-1][0],GPIO.LOW)
          GPIO.output(SENS_LED[num-1][1],GPIO.HIGH)

        elif( stat == LSTAT.YW ):
          GPIO.output(SENS_LED[num-1][0],GPIO.HIGH)
          GPIO.output(SENS_LED[num-1][1],GPIO.HIGH)

        elif( stat == LSTAT.GR_BLK ):
          if( IO.LED_BLINK[num-1] is True ):
            IO.LED_BLINK[num-1] = False
            IO.LED_THRED[num-1].join()
          GPIO.output(SENS_LED[num-1][0],GPIO.LOW)
          GPIO.output(SENS_LED[num-1][1],GPIO.LOW)
          IO.LED_BLINK[num-1] = True
          t=threading.Thread(target=self.BLINK, args=(num,0))
          t.setDaemon(True)
          t.start()
          IO.LED_THRED[num-1] = t

        elif( stat == LSTAT.RD_BLK ):
          if( IO.LED_BLINK[num-1] is True ):
            IO.LED_BLINK[num-1] = False
            IO.LED_THRED[num-1].join()
          GPIO.output(SENS_LED[num-1][0],GPIO.LOW)
          GPIO.output(SENS_LED[num-1][1],GPIO.LOW)
          IO.LED_BLINK[num-1] = True
          t=threading.Thread(target=self.BLINK, args=(num,1))
          t.setDaemon(True)
          t.start()
          IO.LED_THRED[num-1] = t

        else:
          logging.error("LED ERROR")

    def LED_STAT(self,sw):
        if( sw == True ):
            GPIO.output(STAT_LED,GPIO.HIGH)
        else:
            GPIO.output(STAT_LED,GPIO.LOW)

if(__name__ == '__main__'):
    logging.basicConfig(level=logging.DEBUG)

    def btn_rsw(self):
        pass

    def btn_lsw(self):
        pass


    I = IO(rsw_callback=btn_rsw, lsw_callback=btn_lsw)
    for i in range( 1 , 4 ):
        I.LED( i , LSTAT.GR )
        time.sleep( 1 )
        I.LED( i , LSTAT.RD)
        time.sleep( 1 )
        I.LED( i , LSTAT.YW )
        time.sleep( 1 )
        I.LED( i,  LSTAT.GR_BLK )
        time.sleep( 5 )
        I.LED( i,  LSTAT.OFF )
        I.LED( i,  LSTAT.RD_BLK )
        time.sleep( 5 )
        I.LED( i,  LSTAT.OFF )
        time.sleep( 0.5 )


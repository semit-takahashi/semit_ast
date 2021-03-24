#!/usr/bin/python3
#
# 起動時にラズパイの情報をSSD1306に表示

import logging
from libSSD1306 import OLED
from libMachineInfo import getIPAddr,getHostname
import time
import subprocess
import json
import time


if __name__ == '__main__':
    logging.info("STAT start! {}".format( time.strftime("%Y-%m-%d %H:%M:%S") ))
    o = OLED()
    #OLE接続時にステータスを表示
    if( o != None ):
        o.text( 2, 32 , "PLEASE WAIT..." )
        ipAddr = ""
        st_time = time.time()
        while True:
            ipAddr = getIPAddr()
            if( ipAddr != "" ):
                time.sleep(1)
                break

        span = time.time() - st_time 
        logging.info(" - display STATUS {0:5.2f}sec".format(span))
        o.showPI()
    #    time.sleep(10)
    #    print(" - clear Display")
    #    oled.clear()


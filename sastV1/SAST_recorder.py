#!/usr/bin/python3
# SEMI-IT Agriculture Support TOOLs  Recorder
# Ver. 1.0.6 2021/03/23
# Auther F.Takahashi
# 
###### Logging
import logging
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

## import 
from bluepy import btle
from libCloud import sent_Ambient, sent_GAS
from libMachineInfo import getMachine_Temp, sendSIG4Monitor
from libOLED import OLED
from libGPIO2 import IO,LSTAT
from libSQLite import SQL
from libNotify import NOTIFY,getTimeSTR
from libSensor import getEnvdata
#from sensBMP180 import BMP180
from concurrent.futures import ThreadPoolExecutor
import smbus2
import bme280
import time
import sys
import json
import requests
import signal

## settings
sys.path.append('/boot')
from SAST_settings import SENS, AMBIENT, IFTTT, GAS, SAST_NAME, MC_TEMP

######エラー状況
IsERR_SENS = False
IsERR_NET1 = False
IsERR_NET2 = False
IsERR_NET3 = False

###### SIGTERM 
def intr_signal_term(num,frame):
    logging.info("[SAST_recorder] catch SIGTERM")
    sys.exit(1)

signal.signal(signal.SIGTERM, intr_signal_term)

###### GPIO クラス初期 化
gpio = IO()

### === MAIN LOOP 
if __name__ == '__main__':

    num = 0
    sendDATA = {}
    mess = ['','','']
    N = NOTIFY()
    sensValues = []

    # --- センサ読み込み（スレッド処理）
    with ThreadPoolExecutor(max_workers=3 ) as executor:
        futures = []
        num = 0
        for sens in SENS:
            num += 1
            futures.append(executor.submit(getEnvdata, num, sens['MAC'], 'th1'))

        for f in futures:
            sensValues.append(f.result())

    # ---- センサーデータ取得完了
    num = 0
    for sens in SENS:
        num += 1
        sensorValue = sensValues[num-1]
        ## -- 通知用判定処理
        if( sensorValue == False ):
            ## -- Sensor LOST
            N.lost(num)
            continue
        else:
            N.judge(num,sensorValue['Temperature'])

        ## -- 送信データ生成
        if( sens['data'][0] != None ):
            sendDATA[sens['data'][0]] = round(sensorValue['Temperature'],1)

        if( sens['data'][1] != None ):
            sendDATA[sens['data'][1]] = round(sensorValue['Humidity'],1)

    # BME280
    address = 0x76
    bus = smbus2.SMBus(1)
    calibration_params = bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address, calibration_params)
    sendDATA['d8'] = round(data.pressure,1)

    # Machine TEMP
    if( MC_TEMP == 1 ):
        sendDATA['d7'] = round(data.temperature,1)
        logging.info("get Machine temp = {} from BME280".format(sendDATA['d7']))
    else:
        sendDATA['d7'] = getMachine_Temp()
        logging.info("get Machine temp = {} from RaspberryPI".format(sendDATA['d7']))
    
    # -- 時刻の追加
    sendDATA['created'] = getTimeSTR()

    # Ambient
    if( AMBIENT['use'] ):
        ret = sent_Ambient( AMBIENT, sendDATA)
        if( ret == False ):
            IsERR_NET1 = True

    # GAS( Google App Scripts )
    if( GAS['use'] ):
        ret = sent_GAS( GAS, sendDATA )
        if( ret == False ):
            IsERR_NET2 = True

    # Debug Print SendDATA 
    logging.debug( sendDATA )

    # NOTIFY CHECK
    ret = N.send()
    logging.info("Sent IFTTT (ret = {})".format(ret))
    

    # Write SQL
    # net?はIsErrのデターのため、True(=1)が未転送分
    logging.info(f"Write SQLite {sendDATA}")
    sql = SQL()
    sendDATA['net1'] = IsERR_NET1
    sendDATA['net2'] = IsERR_NET2
    sendDATA['net3'] = IsERR_NET3
    sql.append( sendDATA )
    sql.close()

    #OLED
    #num_sens=len(SENS)
    #oled = OLED()
    #oled.showStatus( dt=sendDATA, sens=num_sens, net1=IsERR_NET1, net2=IsERR_NET2  )

    # --- send SIGUSR1 for Monitor
    if( sendSIG4Monitor() == False ):
        logging.warning("Not found Monitor process!!")

    if(IsERR_NET1 or IsERR_NET2):
        logging.warning(f"Network ERROR NET1:{IsERR_NET1} NET2:{IsERR_NET2} NET3:{IsERR_NET3}")
        ## -- Status LED on
        gpio.LED_STAT(True)
        sys.exit(1)

    gpio.LED_STAT(False)
    sys.exit(0)


#### --- History
## Ver.1.0.6
## SIGNAL TERMをフックして終了する様にした


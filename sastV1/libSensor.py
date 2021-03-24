#!/usr/bin/python3
#
import logging
import time
import struct
from bluepy import btle
from libGPIO2 import IO,LSTAT


def getTimeSTR():
    return time.strftime("%Y-%m-%d %H:%M:%S")

''' inkbird IBS-TH1 Access '''
def sens_th1(mac):
    try:
        peripheral = btle.Peripheral(mac)
        characteristic = peripheral.readCharacteristic(0x28)
        (temp, humid, unknown1, unknown2, unknown3) = struct.unpack('<hhBBB', characteristic)
        sensorValue = {
                'created' : getTimeSTR(),
                'Temperature': temp / 100,
                'Humidity': humid / 100,
                'external': unknown1,
                'unknown2': unknown2,
                'unknown3': unknown3,
                'RAW': characteristic,
            }
        return sensorValue

    except btle.BTLEException as e:
        logging.warning("[sens_th1] bulepy Exception:{}"+format(e))
        return None

    except Exception as e:
        logging.error("[sens_th1] Eception :{}"+format(e))
        return None

def getMachineTemp(senstype = 'BME200'):

    # BME280
    if( senstype == 'BME200' ):
        import smbus2
        import bme280
        address = 0x76
        bus = smbus2.SMBus(1)
        calibration_params = bme280.load_calibration_params(bus, address)
        data = bme280.sample(bus, address, calibration_params)
        return  round(data.pressure,1)

    #BMP180
    elif( senstype == 'BMP180' ):
        from libBMP180 import BMP180
        bmp = BMP180()
        if( bmp.inst != None ):
            return round(bmp.getPressure(),1)
        return None

    else: 
        logging.error(f"[getMachineTemp] Notfound senser Type = {senstype}")
        return None


def getEnvdata( num , mac , senstype = 'th1' ):
    logging.debug(f"[getEnvdata] num={num} mac={mac} senstype={senstype}")
    gpio = IO()

    #計測開始時間記録
    #start_time = time.time()

    # LED GREEN点滅
    gpio.LED(num, LSTAT.GR_BLK)

    #計測開始
    if( senstype == 'th1' ):
        sensorValue = sens_th1(mac)
    else:
        logger.error(f"[getEnvdata] unknown sensor type = {senstype}")
        return None

    #取得成功？
    if( sensorValue == None ):
        logging.warning(f"[getEnvdata] {getTimeSTR()} - [{mac}] ERROR!")
        
        # LED RED点滅
        gpio.LED(num, LSTAT.OFF)
        gpio.LED(num, LSTAT.RD_BLK)

        # --- Retyry1 -- after 5sec
        time.sleep(5)

        if( senstype == 'th1' ):
            sensorValue = sens_th1(mac)

        if( sensorValue == None ):
            # ---  Skip 
            logging.error(f"{getTimeSTR()} - [{mac}] 2nd Retry ERROR! -> Skip")
            gpio.LED(num, LSTAT.OFF)
            gpio.LED(num, LSTAT.RD)

            return False
        
    #-- データ取れたので緑点灯
    gpio.LED(num, LSTAT.OFF)
    gpio.LED(num, LSTAT.GR)

    sensorValue['num'] = num
    sensorValue['MAC'] = mac

    logging.debug(sensorValue)

    return  sensorValue

''' this function is running must by ROOT user'''
def getBattery_th1( MACS ):
    logging.debug("[getBattery_th1] scanning ...")
    BATTS = []
    scn = btle.Scanner()
    # -- 10秒スキャン
    devs = scn.scan(10.0)
    logging.debug(f"[getBattery_th1] scan complete > {len(devs)} ")
    stime = getTimeSTR()
    for dev in devs:
        val = dev.getValueText(255)
        logging.debug(f"[getBattery_th1] {dev.addr} > {val}")
        if( val is None or len(val) != 18):
            continue
        (temp,humid,ext,uk1,uk2,batt,uk3) = struct.unpack('<hhBBBBB', bytes.fromhex(val))
        temp /=100
        humid /=100
        rssi = dev.rssi
        eSens = True if ext == 1 else False
        BATTS.append({'MAC':dev.addr.upper(),'battery':batt,'temp':temp,'humid':humid,'ext':eSens,'rssi':rssi,'created':stime})
    logging.debug(BATTS[-1])
            
    ret = []
    for mac in MACS:
        for bat in BATTS:
            if( mac.upper() == bat['MAC'] ):
                ret.append(bat)
    return ret
         
if __name__ == '__main__':
    # センサー値同時取得
    from concurrent.futures import ThreadPoolExecutor
    import  sys
    #settings
    sys.path.append('/boot')
    from SAST_settings import SENS, AMBIENT, IFTTT, GAS, SAST_NAME, MC_TEMP

    logging.basicConfig(level=logging.DEBUG)

    # --- BATTERY
    macs = []
    for s in SENS:
        macs.append(s['MAC'])
    ret = getBattery_th1(macs)
    logging.info(f"RET = {ret}")
    from libSQLite import SQL
    S = SQL()
    for bat in ret:
        S.updateBattery( bat )


    sys.exit(0)
    # 同時にセンサーデータを取得
    with ThreadPoolExecutor(max_workers=3 ) as executor:
        futures = []
        num = 0
        for sens in SENS:
            num += 1
            futures.append(executor.submit(getEnvdata, num, sens['MAC'], 'th1'))
        logging.info("submit end")
        num = 0
        for f in futures:
            num += 1
            print(f"num={num}  res:{f.result()}")
    logging.info("main end")

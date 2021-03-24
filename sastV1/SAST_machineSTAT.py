#!/usr/bin/python3
#
import logging
import sys
from libSensor import getBattery_th1
from libSQLite import SQL

#settings
sys.path.append('/boot')
from SAST_settings import SENS, AMBIENT, IFTTT, GAS, SAST_NAME, MC_TEMP

###### Logging
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

if __name__ == '__main__':
   ## --- バッテリーステータス更新
   macs = []
   S=SQL()
   for mac in SENS:
       macs.append(mac['MAC'])
   logging.info(f"get Battery STASUS MAC={macs}") 

   batts = getBattery_th1( macs )
   for batinfo in batts:
       logging.info(f" {batinfo['MAC']} {batinfo['battery']}%  {batinfo['rssi']}dBm") 
       S.updateBattery( batinfo )


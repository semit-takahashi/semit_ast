#!/usr/bin/python3
#
import logging
from libSQLite import SQL 

import sys
import time
from datetime import datetime, timezone, timedelta
import requests
from enum import IntEnum

#settings
sys.path.append('/boot')
from SAST_settings import SENS, AMBIENT, IFTTT, LINE, GAS, SAST_NAME

logging.basicConfig(level=logging.INFO)

''' センサー状態Enum（DATABASE用) '''
class SENS_ST(IntEnum):
    NONE = -1,
    LOST = 0,
    NORMAL = 1,
    LOW_WARN = 2,
    LOW_CAUTION = 3,
    HIGH_WARN = 4,
    HIGH_CAUTION = 5,

''' ライブラリ：SQL用文字列時刻をdatetime(native)型に変換 ''' 
def str2time( str ):
    try:
        dt = datetime.strptime(str+'+0900', "%Y-%m-%d %H:%M:%S%z")
        return dt
    except Exception as e:
        logging.error(f"[str2time] ERROR : str={e}")
        return None

''' ライブラリ；現在時刻の文取得 '''
def getTimeSTR():
    return time.strftime("%Y-%m-%d %H:%M:%S")

    
''' メッセージ通知用クラス（IFTTT利用） ''' 
class NOTIFY:
    S = SQL()
    IsNOTIFY = False
    
    def __init__(self):
        pass

    def judge(self, sensID, value):
        logging.debug(f"[judge] sens={sensID} value={value}")
        mess = None
        THR = None
        latest = self.S.notify(sensID)
        if( 1 <= sensID <= 3 and latest != None ):
            sens = SENS[sensID-1]
            #logging.debug(f"SENS[{sensID-1}]: {sens['th']}")
        else:
            logging.error(f"[NOTIFY] judge - over rage senseor ID = {sensID}")
            return
        
        if( sens['th'][0] != None ):
            #logging.debug("define sens LOW threthold.")
            # -- LOW 0 - CAUTION 1
            if( sens['th'][0][1] >= value ):
                latest['state'] = SENS_ST.LOW_CAUTION
                latest['nstate'] = SENS_ST.LOW_CAUTION
                mess = f"🟥警告!【{sens['name']}】が{sens['th'][0][1]}℃を下回りました(現在{value}℃)\n"
                latest['message'] = mess
                latest['ntime'] = None
                self.S.update_notify(latest)
                logging.debug(mess)
                NOTIFY.IsNOTIFY = True
                return
            # -- LOW 0 - WARNING 1
            if( sens['th'][0][0] >= value ):
                latest['state'] = SENS_ST.LOW_WARN
                mess = f"🟠注意!【{sens['name']}】が{sens['th'][0][0]}℃を下回りました(現在{value}℃)\n"
                if( latest['ntime'] == None or self.IsIntervalWarn( latest['ntime'] ) ):
                    latest['message'] = mess
                    latest['nstate'] = SENS_ST.LOW_WARN
                    latest['ntime'] = None
                    NOTIFY.IsNOTIFY = True
                self.S.update_notify(latest)
                logging.debug(mess)
                return

        if( sens['th'][1] != None ):
            #logging.debug("define sens HIGH threthold.")
            # -- HIGH 1 - CAUTION 1
            if( sens['th'][1][1] <= value ):
                latest['state'] = SENS_ST.HIGH_CAUTION
                latest['nstate'] = SENS_ST.HIGH_CAUTION
                mess = f"🟥警告!【{sens['name']}】が{sens['th'][1][1]}℃を超えました(現在{value}℃)\n"
                latest['message'] = mess
                latest['ntime'] = None
                self.S.update_notify(latest)
                logging.debug(mess)
                NOTIFY.IsNOTIFY = True
                return
            # -- HIGH 1 - WARNING 0
            if( sens['th'][1][0] <= value ):
                latest['state'] = SENS_ST.HIGH_WARN
                mess = f"🟠注意!【{sens['name']}】が{sens['th'][1][0]}℃を超えました(現在{value}℃)\n"
                if( latest['ntime'] == None or self.IsIntervalWarn( latest['ntime'] ) ):
                    latest['message'] = mess
                    latest['nstate'] = SENS_ST.LOW_WARN
                    latest['ntime'] = None
                    NOTIFY.IsNOTIFY = True
                self.S.update_notify(latest)
                logging.debug(mess)
                return

        latest['state'] = SENS_ST.NORMAL
        latest['nstate'] = SENS_ST.NORMAL
        latest['message'] = None
        latest['ntime'] = None
        logging.debug("discard Notify.") 
        self.S.update_notify(latest)
        return

    ''' sensor lost '''
    def lost(self,sensID):
        logging.info(f"sens NO{sensID} LOST")
        latest = self.S.notify(sensID)
        logging.info(f"-> latest{latest}")
        if( latest['state'] != SENS_ST.LOST ):
            latest['state'] = SENS_ST.LOST
            latest['nstate'] = SENS_ST.LOST
            latest['ntime'] = getTimeSTR()
            latest['message'] = f"‼️センサー【{SENS[sensID-1]['name']}】と接続できません\n"
            logging.info(f"call Update Notify {latest}")
            self.S.update_notify(latest)

    '''IFTTT POST '''
    def POST_IFTTT(self,mess):
        if( IFTTT["use"] == False ) :
            return
        try:
            data = {'value1':f"{SAST_NAME}",'value2':f"{mess}",'value3':f"{IFTTT['LINK']}"}
            head = "Content-Type: application/json"
            print(data)
            r_post = requests.post( IFTTT["URL"], json = data)
        except Exception as e:
            logging.error(f"IFTTT Exception: {e}")
            return None
        return r_post.status_code


    ''' LINE POST '''
    def POST_LINE(self,mess):
        if( LINE['use'] == False ):
            return
        try:
            m = f"{SAST_NAME}\n{mess}\n📊グラフ\n{LINE['LINK']}"
            url = 'https://notify-api.line.me/api/notify'
            headers = {'Authorization': f'Bearer {LINE["token"]}'}
            data = {'message': {m}}
            print(data)
            r_post = requests.post(url, headers = headers, data = data)
        except Exception as e:
            logging.error(f"LINE Notify Exception: {e}")
            return None
        return r_post.status_code


    ''' 通知の送信（存在する場合） '''
    def send(self):
        #logging.debug("[send]")
        ntime = getTimeSTR()
        mess = []
        for sensID in range( 1 , 4 ):
            row = self.S.notify(sensID)
            logging.debug(f"send - ID:{sensID} - {row}")
            if( row['nstate'] != SENS_ST.NORMAL and row['nstate'] != SENS_ST.NONE ):
                if( row['ntime'] == None ):
                    ## -- 通知があるので通知
                    logging.info(f"Notify send {sensID} -- {SENS_ST(row['nstate']).name}")
                    mess.append( row['message'])
                    self.S.update_notifyTime(sensID, ntime)
                elif( row['state'] == SENS_ST.LOST and self.IsIntervalWarn( row['ntime'] ,interval = 600 )):
                    ## --- センサーが10分以上発見できない
                    logging.info(f"Notify LOST send {sensID} -- {SENS_ST(row['nstate']).name}")
                    mess.append( row['message'] )
                    self.S.update_notifyTime(sensID, ntime)
                
        message = ''.join(mess)
        if( message != '' ):
            ret  = self.POST_IFTTT(message)
            ret  = self.POST_LINE(message)
            #logging.debug(f"[send](ret={ret}) {SAST_NAME} {message}")
            NOTIFY.IsNOTIFY = False
            return True

        return False

## TODO -- バッテリー状態をIFTTに通知する関数

    def debug_print(self,sensID):
        row = self.S.notify(sensID)
        print(row)


    def debug_updateNtime(self, sensID):
        self.S.update_notifyTime(sensID)


    ''' 注意時間間隔の計算（必要ならTrue） '''
    def IsIntervalWarn( self, lastTime, interval = 300 ):
        last = str2time(lastTime)
        JST = timezone(timedelta(hours=+9), 'JST')
        span = datetime.now(JST) - last
        logging.info(f"[IsIntervalWarn] str={lastTime} int={interval}sec span={span.seconds}sec")
        if( span.seconds >= interval ):
            return True
        return False


### -- 単体テスト
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("libNotify test")
    N=NOTIFY()
    mess = "通知メッセージのテスト\nメッセージテスト"
    N.POST_IFTTT(mess)
    N.POST_LINE(mess)


    '''
    sensID = 1
    value = 10
    N.debug_print(sensID)
    N.judge(sensID,value)
    N.debug_print(sensID)
    #N.debug_updateNtime(sensID)
    N.debug_print(sensID)
  
    print("\n\n RANGE TEST NO2\n\n")
    for n in range( -2 , 50 ,2 ):
        N.judge(2,n)
        #N.debug_print(sensID)

    print("\n\n RANGE TEST NO3 \n\n")
    for n in range( -2 , 50 ,2 ):
        N.judge(3,n)

    print(f"NOTIFY ? {N.IsNOTIFY}")
    N.send()
    '''


#!/usr/bin/python3
import logging
import ambient
import requests
import time
import json

# Ambientにデータを書き込む（送信する）
def sent_Ambient( amDATA, sendDATA):
    # create Ambient Object
    am = ambient.Ambient(amDATA['channelID'], amDATA['WriteKEY'])

    #データの作成 dictionaryで作成する
    #データはd1~d8として作成する。
    #ローカルタイムスタンプは 'created': 'YYYY-MM-DD HH:mm:ss.sss' として作成する。
    
    for retry in range(6):
        # 10秒間隔で6回リトライ
        try:
            ret = am.send(sendDATA)
            logging.info("sent to Ambient (ret = {0})".format(ret.status_code))
            return True

        except requests.exceptions.RequestException as e:
            logging.error("[Ambient] request failed : {0}".format(e))
            time.sleep(10)

        except Exception as e:
            logging.error("[Ambient] Exception : {0}".format(e))

    return False

# Google App Scripts(GAS）にデータを転送する
def sent_GAS( GAS, sendDATA):

    for retry in range(5):
        # 10秒間隔で6回リトライ
        try:
            ret = requests.post(GAS['URL'], data=json.dumps(sendDATA), headers={'Content-Type': 'application/json'})
            logging.info("sent to GAS (ret = {0})".format(ret.status_code))
            return True

        except Exception as e:
            logging.error("[GAS] request faild  : {0}".format(e))
            time.sleep(10)

    return False


if __name__ == '__main__':
    # Unit TEST Code
    pass


#!/usr/bin/python3
#
# --- 本体名称
SAST_NAME = "SAST 1号機"

### ---- INKBIRD MAC Address 
### センサーのリスト
## S   :センサータイプ（IBS-TH1:th1)
## MAC :MACアドレス
## name:センサ名称（未利用）
## data:Ambientへの送信データの紐付け d1~d6 1(d7気圧、d8本体温度として固定）
## th  :閾値 L=LOW値/H=HIGH値 ( WARN（注意）, CAUTION（警告）)にて記載
##      利用しない場合はNoneとする#
SENS = [
{ 'S':'th1','MAC':'64:69:4E:9D:20:59','name':"苗箱",
    'data':[ 'd1', 'd2'], 'th':[None,( 30, 35 )] },
{ 'S':'th1','MAC':'10:08:2C:1F:6B:A2','name':"ハウス内",
    'data':[ 'd3', 'd4'], 'th':[( 5 , 0 ),( 40, 50 )] },
{ 'S':'th1','MAC':'10:08:2C:1F:32:9C','name':"外気温",
    'data':[ 'd5', 'd6'], 'th':[None,None] },
]

### Ambient設定情報
## use : 使う場合にTrue 
## channelID : チャンネルID
## WriteKEY :ライトキー
## ReadKEY　:リードキー（未利用）
# -- メモ：育苗ハウス＠宮城県栗原市
# https://ambidata.io/bd/board.html?id=22517 
AMBIENT = {
    'use'       : True ,
    'channelID' : 32336,
    'WriteKEY'  : '687f3dc3b44ab97b',
    'ReadKEY'   : 'fbe413b00ddc4e25',
}

### IFTTT 設定情報
## use  : 使う場合にTrue
## URL  : 送信先URL（WebHookのDocument参照）
## LINK : グラフ描画サイトのURL
IFTTT = {
    'use'  : False ,
    'URL'  : 'https://maker.ifttt.com/trigger/SAST01/with/key/dhSeRWgvWLZFxSoTdUa_EK',
    'LINK' : 'https://ambidata.io/bd/board.html?id=22517'
}

### LINE Notify 設定情報
## use   : 使う場合にTrue
## token : 通知用TOKEN（LINE Notify APIにて取得する）
## LINK  : グラフ描画サイトのURL
LINE = {
    'use'  : True,
    'token': 'WajDPDSEvFdvkOlLDpIIYn5VVzBwfJ03uwzwprepzFX',
    'LINK' : 'https://ambidata.io/bd/board.html?id=22517'
} 

### Google Spreadsheet 
## use : 使う場合
## URL : 
GAS = {
   'use' : True ,
   'URL' : 'https://script.google.com/macros/s/AKfycbzNBUnFYXLDbi2k4_6a2VlSZTKMO7O-xkUbawxQuhzPdWMJf08z58sYvA/exec',
}


#### 本体温度センサー ####
## どちらか一方をコメントアウト
#MC_TEMP = 0  # CPU
MC_TEMP = 1  # BMP280



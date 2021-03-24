#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Recorder Liblary
# Auther: Fumihito.Takahashi SEM-IT

# sqlite3 標準モジュールをインポート
import logging
import sqlite3
import time
DB_PATH = '/home/pi/recode.sqlite'

class SQL:
  connection = None
  ''' 初期化 '''
  def __init__(self):
    logging.debug(f"SQL : __init__ DB_PATH={DB_PATH}")
    self.connection = sqlite3.connect(DB_PATH)
    #self.connection.isolation_level = None
    c = self.connection.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS data ( id INTEGER UNIQUE, created TEXT NOT NULL, d1 REAL, d2 REAL, d3 REAL, d4 REAL, d5 REAL, d6 REAL, d7 REAL, d8 REAL, d9 REAL, opt1 TEXT, opt2 TEXT, opt3 TEXT, net1 INTEGER , net2 INTEGER , net3 INTEGER, PRIMARY KEY(id AUTOINCREMENT))")
    self.connection.commit()
    c.execute("CREATE TABLE IF NOT EXISTS notify ( id INTEGER UIQUE, state INTEGER NOT NULL, ntime TEXT, nstate INTEGER, message TEXT, PRIMARY KEY(id))")
    self.connection.commit()
    c.execute("SELECT id from notify")
    if( c.fetchone() == None ):
        logging.debug("DB is NEW - INSERT notify DATA")
        c.execute("INSERT INTO notify ( id, state, nstate ) VALUES( 1, -1, -1 )")
        c.execute("INSERT INTO notify ( id, state, nstate ) VALUES( 2, -1, -1 )")
        c.execute("INSERT INTO notify ( id, state, nstate ) VALUES( 3, -1, -1 )")
        self.connection.commit()
    c.execute("CREATE TABLE IF NOT EXISTS battery ( mac TEXT NOT NULL, created TEXT NOT NULL, battery INTEGER NOT NULL, temp INTEGER, humid INTEGER, ext INTEGER, rssi INTEGER, PRIMARY KEY(mac))")
    self.connection.commit()
    

  ''' レコード追加 '''
  def append(self, data):
    logging.debug("SQL: append {}".format(data))
    try:
      columns = ', '.join(data.keys())
      placeholders = ':'+', :'.join(data.keys())
      query = 'INSERT INTO data (%s) VALUES (%s)' % (columns, placeholders)
      logging.debug("QUERY = {}".format(query))
      c = self.connection.cursor()
      c.execute(query, data)
      self.connection.commit()
    except sqlite3.Error as e:
      logging.error("sqlite3 insert ERROR:{0}".format(e))
      return False

  ''' 利用終了時に呼び出し（クローズ） '''
  def close(self):
    self.connection.close()

  ''' get NET1 Error Recorde '''
  def get_NET1_Error(self):
    logging.debug("[SQL] get_NET1_Error()")
    try:
      c = self.connection.cursor()
      c.execute("SELECT * FROM DATA WHERE net1=1")
    except sqlite3.Error as e:
      logging.error("---sqlite3 SELECT ERROR:{0}".format(e))
      return None
    data = []
    for d in c.fetchall():
        data.append(self.encode_data(d))
    return data

  def update_NET1(self,ids):
    logging.debug(f"[SQL] update_NET1 id=(len(ids))")
    try:
      c = self.connection.cursor()
      for i in ids:
          c.execute(f"UPDATE data SET net1=0 WHERE id={i}")
      self.connection.commit()
    except sqlite3.Error as e:
      logging.error("---sqlite3 SELECT ERROR:{0}".format(e))
      return None
    return


  ''' get NET2 Error Recorde '''
  def get_NET2_Error(self):
    logging.debug("[SQL] get_NET2_Error()")
    try:
      c = self.connection.cursor()
      c.execute("SELECT * FROM DATA WHERE net2=1")
    except sqlite3.Error as e:
      logging.error("---sqlite3 SELECT ERROR:{0}".format(e))
      return None
    data = []
    for d in c.fetchall():
        data.append(self.encode_data(d))
    return data

  def update_NET2(self,ids):
    logging.debug(f"[SQL] update_NET2 id=(len(ids))")
    try:
      c = self.connection.cursor()
      for i in ids:
          c.execute(f"UPDATE data SET net2=0 WHERE id={i}")
      self.connection.commit()
    except sqlite3.Error as e:
      logging.error("---sqlite3 SELECT ERROR:{0}".format(e))
      return None
    return


  ''' get NET3 Error Recorde '''
  def get_NET3_Error(self):
    logging.debug("[SQL] get_NET3_Error()")
    try:
      c = self.connection.cursor()
      c.execute("SELECT * FROM DATA WHERE net3=1")
    except sqlite3.Error as e:
      logging.error("---sqlite3 SELECT ERROR:{0}".format(e))
      return None
    data = []
    for d in c.fetchall():
        data.append(self.encode_data(d))
    return data

  def update_NET3(self,ids):
    logging.debug(f"[SQL] update_NET3 id=(len(ids))")
    try:
      c = self.connection.cursor()
      for i in ids:
          c.execute(f"UPDATE data SET net3=0 WHERE id={i}")
      self.connection.commit()
    except sqlite3.Error as e:
      logging.error("---sqlite3 SELECT ERROR:{0}".format(e))
      return None
    return

  ''' 最新レコードを取得(dict形式) '''
  def latest(self):
    logging.debug("[SQL] latest")
    try:
      c = self.connection.cursor()
      c.execute("SELECT * FROM DATA ORDER BY created DESC LIMIT 1")
    except sqlite3.Error as e:
      logging.error("---sqlite3 SELECT ERROR:{0}".format(e))
      return None
    return self.encode_data(c.fetchone())

  ''' 最新レコードのIDを取得 '''
  def latestID(self):
    logging.debug("SQL: latestID")
    try:
      c = self.connection.cursor()
      c.execute("select * from data order by created  DESC LIMIT 1")
    except sqlite3.Error as e:
      logging.error("sqlite3 select ERROR:{0}".format(e))
      return None
    return c.fetchone()[0]

  ''' 通知データのレコード取得(id指定) '''
  def notify(self,sensID):
    #logging.debug(f"[SQL] notify {sensID}")
    try:
      c = self.connection.cursor()
      c.execute(f"SELECT * FROM NOTIFY WHERE id = {sensID}") 
    except sqlite3.Error as e:
      logging.error("---sqlite3 select ERROR:{0}".format(e))
      return None
    return self.encode_notify(c.fetchone())
 
  ''' notifyの更新 '''
  def update_notify(self,d):
    logging.debug(f"[SQL]: update_notify d={d}")
    if( d['nstate'] == None ):
      ## --- 状態変更のみ
      try:
        c = self.connection.cursor()
        c.execute(f"UPDATE notify set state=?, message=? where id={d['id']}",(d['state'], d['message']))
        self.connection.commit()
      except sqlite3.Error as e:
        logging.error("---sqlite3 UPDATE state  ERROR:{0}".format(e))
        return False

    else:
      ## --- 通知実行  time(TEXT)にNoneを入れる場合は、formatは使えないので注意
      try:
        c = self.connection.cursor()
        c.execute(f"UPDATE notify set state=?, ntime=?, nstate=?, message=? where id={d['id']}",(d['state'],d['ntime'],d['nstate'],d['message']))
        self.connection.commit()
      except sqlite3.Error as e:
        logging.error("---sqlite3 UPDATE all ERROR:{0}".format(e))
        return False

    return True

  ''' notifyの更新 通知時間のみ'''
  def update_notifyTime(self,sensID,ntime=None):
      if( ntime == None ):
          ntime = time.strftime("%Y-%m-%d %H:%M:%S")
      try:
        logging.debug(f"[update_notifyTime] is={sensID}  ntime={ntime}")
        c = self.connection.cursor()
        c.execute("UPDATE notify set ntime=? where id=?",(ntime,sensID))
        self.connection.commit()
      except sqlite3.Error as e:
        logging.error("---sqlite3 UPDATE ntime ERROR:{0}".format(e))
        return False

      return True


  ''' notifyのエンコード 取得したデータをdictに変換 '''
  def encode_notify(self,d):
    if( d == None ):
        return None
    ret = {}
    ret['id'] = d[0]
    ret['state'] = d[1]
    ret['ntime'] = d[2]
    ret['nstate'] = d[3]
    ret['message'] = d[4]
    return ret

  ''' dataのエンコード 取得したデータをdictに変換 '''
  def encode_data(self,d):
    if( d == None ):
        return None
    ret = {}
    ret['id'] = d[0]
    ret['created'] = d[1]
    ret['d1'] = d[2]
    ret['d2'] = d[3]
    ret['d3'] = d[4]
    ret['d4'] = d[5]
    ret['d5'] = d[6]
    ret['d6'] = d[7]
    ret['d7'] = d[8]
    ret['d8'] = d[9]
    ret['d9'] = d[10]
    ret['opt1'] = d[11]
    ret['opt2'] = d[12]
    ret['opt3'] = d[13]
    ret['net1'] = d[14]
    ret['net2'] = d[15]
    ret['net3'] = d[16]
    return ret

  def getBattery(self, MAC ):
    logging.debug(f"SQL[getBattery] {MAC}")
    try:
      c = self.connection.cursor()
      c.execute(f"SELECT battery,rssi FROM battery WHERE mac='{MAC}'")
    except sqlite3.Error as e:
      logging.error("sqlite3 select ERROR:{0}".format(e))
      return None
    bat = c.fetchone()
    if( bat is not None):
        return bat
    return None

  def updateBattery(self, data ):
    logging.debug(f"SQL[updateBattery] {data}")
    try:
      cols = ', '.join(data.keys())
      places = ':'+', :'.join(data.keys())
      ext = 1 if data['ext'] == True else 0
      query ="INSERT INTO battery ({0}) VALUES ({1}) ON CONFLICT(MAC) DO UPDATE SET battery={2},temp={3},humid={4},ext={5},rssi={6},created='{7}';".format(cols, places,data['battery'],data['temp'],data['humid'],ext,data['rssi'],data['created'])
      c = self.connection.cursor()
      c.execute(query, data)
      self.connection.commit()
    except sqlite3.Error as e:
      logging.error("sqlite3 select ERROR:{0}".format(e))
      return None
    return True

      
  def sample_insert(self):
      logging.debug("sample insert")
      data = { 'created': "2021/02/27 21:22:10",'d1':19.3,'d2':45.7,'d3':7.7,'d4':53.1,'d8':1012.9,'net1':1,'net2':1,'net3':1}
      self.append( data )


      data = { 'created': "2021/02/26 21:24:09",'d1':19.2,'d2':45.5,'d3':7.7,'d4':53.7,'d8':1013.1,'net1':1,'net2':1,'net3':1}
      print(data)
      self.append( data )
     
      data = { 'created': "2021/02/25 21:26:10",'d1':19.2,'d2':45.6,'d3':7.7,'d4':54.1,'d8':1012.9,'net1':0,'net2':0,'net3':1}
      print(data)
      self.append( data )

      data = { 'created': "2021/02/24 21:28:08",'d1':19.2,'d2':45.4,'d3': 7.7,'d4':54.2,'d8':1012.9,'net1':1,'net2':0,'net3':1}
      print(data)
      self.append( data )

  def __del__(self):
    logging.debug("[SQL] call del()")
    self.close()

  
if __name__ == '__main__':
    import sys
    # for test
    logging.basicConfig(level=logging.DEBUG)
    S = SQL()
    #S.sample_insert()
    ret = S.latest()
    print(f"LATEST is {ret}")

    ret = S.get_NET1_Error()
    if( len(ret) != 0 ):
        print(f"NET1 Error = {len(ret)}")

        i = []
        for d in ret:
            i.append(d['id'])
        print(i)
        S.update_NET1(i)
    else:
        print("NET1 no ERROR")

    ret = S.get_NET2_Error()
    if( len(ret) != 0 ):
        print(f"NET1 Error = {len(ret)}")

        i = []
        for d in ret:
            i.append(d['id'])
        print(i)
        S.update_NET2(i)
    else:
        print("NET2 no ERROR")

    sys.exit(0)

    print("STATE test")
    ret = S.notify(1)
    print(ret)
    ret = S.notify(2)
    print(ret)
    ret = S.notify(3)
    print(ret)
    ret = S.notify(0)
    print(ret)

#!/usr/bin/python3
#
import sys
sys.path.append('/boot')
from  SAST_settings import SAST_NAME,SENS,AMBIENT,IFTTT,GAS

if __name__ == '__main__' :
    print('SEM-IT Agriculture Support Tools SAST Info View')
    print("")
    print("[SAST NAME]")
    print(SAST_NAME)
    print("")
    print("[Sensors]")
    for S in SENS:
        print("{} - {} / {} / data {}".format(S['S'], S['name'], S['MAC'], S['data']))
        if( S['th'][0] != None ):
            print("  Alert LOW   WARN:{0:3d} CAUTION:{1:3d}".format(S['th'][0][0], S['th'][0][1]))
        if( S['th'][1] != None ):
            print("  Alert HIGHT WARN:{0:3d} CAUTION:{1:3d}".format(S['th'][1][0], S['th'][1][1]))
    print("")
    print("[Ambient]")
    print(" use      : {}".format(AMBIENT['use']))
    print(" channelID: {}".format(AMBIENT['channelID']))
    print(" WriteLEY : {}".format(AMBIENT['WriteKEY']))
    print(" ReadKEY  : {}".format(AMBIENT['ReadKEY']))
    print("")
    print("[IFTTT]")
    print(" use    : {}".format(IFTTT['use']))
    print(" URL    : {}".format(IFTTT['URL']))
    print(" LINK   : {}".format(IFTTT['LINK']))
    print("")
    print("[GAS( Google App Script )]")
    print(" use : {}".format(GAS['use']))
    print(" URL : {}".format(GAS['URL']))
    print("")

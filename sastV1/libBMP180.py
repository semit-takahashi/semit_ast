#!/usr/bin/python3
#
import logging
import Adafruit_BMP.BMP085 as BMP085


class BMP180:
    inst = None

    def __init__(self):
        try:
            self.inst = BMP085.BMP085()

        except Exception as e:
            logging.error(f"BMP180 Init Exception({e})"e))
            self.inst = None

    def getTemperature(self):
        if( self.inst == None ):
            return None
        return round( self.inst.read_temperature() ,1 )

    def getPressure(self):
        if( self.inst == None ):
            return None
        return round(self.inst.read_pressure() / 100.0 ,1)
        
    def getAltitude(self):
        if( self.inst == None ):
            return None
        return round( self.inst.read_altitude() ,2)

    def getSeaLevelPressure(self):
        if( self.inst == None ):
            return None
        return round( self.inst.read_sealevel_pressure() / 100.0 ,1)

if __name__ = '__main__':
        bmp = BMP180()
        if( bmp.inst != None ):
            print( 'Temp = {0} C'.format( self.getTemperature()))
            print( 'Pressure = {0} hPa'.format( self.getPressure() ) )
            print( 'Altitude = {0} m'.format( self.getAltitude() ) )
            print( 'Sealevel Pressure = {0} hPa'.format(self.getSeaLevelPressure()) )


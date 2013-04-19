import Sensors
from BajaDevices import timer
import FileIO, os
from BajaMessages import *
from Dashboard import *

talker = FileIO.Talker([TachometerMessage,SpeedometerMessage,GPSMessage])
logger = FileIO.Logger([TachometerMessage,SpeedometerMessage,GPSMessage],filePrefix = '/home/phoenix/Data/')

timer.start()
tach = Sensors.Tachometer(15)
speedo = Sensors.Speedometer(16)
aGps = Sensors.GPS()
dash = Dashboard()

tach.start()
speedo.start()
aGps.start()
dash.start()

try:
	while True:
		pass
except KeyboardInterrupt:
	tach.stop()
	speedo.stop()
	aGps.stop()
	dash.stop()

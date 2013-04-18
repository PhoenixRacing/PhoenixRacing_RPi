import Sensors
from BajaDevices import timer
import FileIO

talker = FileIO.Talker(['gps','tach','speedo'])

timer.start()
tach = Sensors.Tachometer(15)
speedo = Sensors.Speedometer(16)
aGps = Sensors.GPS()

tach.start()
speedo.start()
aGps.start()

try:
	while True:
		pass
except KeyboardInterrupt:
	tach.stop()
	speedo.stop()
	aGps.stop()

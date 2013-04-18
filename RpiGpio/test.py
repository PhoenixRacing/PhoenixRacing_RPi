from BajaSensors import GPS, Tachometer
from RpiGpioObject import IO_TYPES
import time



tach = Tachometer(11)
speedo = Tachometer(12)
aGPS = GPS()

aGPS.start()
tach.start()
speedo.start()

try:
	while True:
		time.sleep(1)
		print aGPS
		print tach.get()
		print speedo.get()
except KeyboardInterrupt:
	aGPS.stop()
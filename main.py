from BajaSensors import *
import time

tach = Tachometer(11)

tach.start()

while True:
	try:
		time.sleep(.1)
	except KeyboardInterrupt, SystemExit:
		tach.stop()
		break
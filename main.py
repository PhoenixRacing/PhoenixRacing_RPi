from BajaSensors import *
import time

tach = Tachometer(11)

tach.start()

while True:
	try:
		time.sleep(.1)
		print tach.get()
	except KeyboardInterrupt, SystemExit:
		tach.stop()
		break

from BajaSensors import *
import time

tach = Tachometer(11)
speedo = Tachometer(12)


tach.start()
speedo.start()

while True:
	try:
		time.sleep(1)
		print tach.get(),'   ', speedo.get()
	except KeyboardInterrupt, SystemExit:
		tach.stop()
		speedo.stop()
		break

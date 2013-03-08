from RpiGpioObject import *
import datetime, time

class Tachometer(RpiGpioDevice):
	"""docstring for Tachometer"""
	def __init__(self, pin):
		super(Tachometer, self).__init__({pin:True})
		self.alive = True
		self.lastEdgeTime = datetime.datetime.now()
		self.updateTime = .01

	def run(self):
		while self.alive:
			print 'I\'m alive'
			time.sleep(self.updateTime)


	def stop(self):
		self.alive = False

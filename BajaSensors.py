from RpiGpioObject import *
import datetime

class Tachometer(RpiGpioDevice):
	"""docstring for Tachometer"""
	def __init__(self, pin):
		super(Tachometer, self).__init__({pin:True})
		self.alive = True
		self.lastEdgeTime = datetime.datetime.now()
		self.updateTime = 

	def run(self):
		while self.alive:
			print 'I\'m alive'


	def stop(self):
		self.alive = False

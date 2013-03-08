from RpiGpioObject import *
import datetime, time

class Tachometer(RpiGpioDevice):
	"""docstring for Tachometer"""
	def __init__(self, pin):
		super(Tachometer, self).__init__({pin:True})
		self.alive = True
		self.lastRisingEdgeTime = datetime.datetime.now()
		self.updatePeriod = .01
		self.lastState = self.pins[0].get()
		self.averagedRPM = 0
		self.numberOfMagnets = 2
		self.alpha = .33

	def get(self):
		return self.averagedRPM

	def run(self):
		while self.alive:
			now = datetime.datetime.now()
			state = self.pins[0].get()

			#an edge of the magnet
			if state is not self.lastState:
				self.lastState = state
	
				#a rising edge of the magnet
				if not state:
					dt = max(1, (now - self.lastRisingEdgeTime).microseconds)/1000000.0
					rpm = 60.0 / self.numberOfMagnets / dt
					self.averagedRPM = self.averagedRPM*(1-self.alpha) + rpm*self.alpha
					self.lastRisingEdgeTime = now

			#catch the case when the input stops
			elif now - self.lastRisingEdgeTime > datetime.timedelta(seconds=0.25):
				print 'too slow'
				self.averagedRPM = max(1e-4,(self.averagedRPM * 2) / 3)
				self.lastRisingEdgeTime = now

	def stop(self):
		self.alive = False

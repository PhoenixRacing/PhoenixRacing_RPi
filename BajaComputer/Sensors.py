import RPi.GPIO as GPIO
from BajaDevices import *
from dateutil import tz
import time, gps, datetime

GPIO.setmode(GPIO.BOARD)

class Sensor(BajaDevice):
	def __init__(self):
		super(Sensor,self).__init__()

class Tachometer(Sensor):
	def __init__(self, pin):
		super(Tachometer,self).__init__()
		self.pin = pin
		GPIO.setup(pin, GPIO.IN)

		self.lastInputTime = manager.timer.getTime()
		self.state = self.getState()
		self.numberOfMagnets = 2
		self.averagedRPM = 0
		self.alpha = 0.33
		
	def getState(self):
		return GPIO.input(self.pin)

	def run(self):
		while self.alive:

			now = manager.timer.getTime()
			if self.state is not self.getState():
				self.state = not self.state
				

				if not self.state:
					dt = max(1, (now - self.lastInputTime).microseconds)/1000000.0
					rpm = 60.0 / self.numberOfMagnets / dt
					self.averagedRPM = self.averagedRPM*(1-self.alpha) + rpm*self.alpha
					self.lastInputTime = now

					self.publish()
					#todo set/reset the timer callback to set the rpm to 0
					
	def publish(self):
		manager.publish('tach',{'rpm':self.averagedRPM})

class Speedometer(Tachometer):
	def __init__(self,pin,gearRatio = 11,tireRadius=26):
		super(Speedometer,self).__init__(pin)
		self.gearRatio = gearRatio
		self.tireRadius = tireRadius
		self.groundSpeed = 0

	def publish(self):
		self.groundSpeed = self.averagedRPM*2*math.pi*tireRadius*(1/12.0)*(1/5280.0)*(60)/self.gearRatio
		manager.publish('speedo',{'rpm':self.averagedRPM, 'speed':self.groundSpeed})

				

class GPS(Sensor):
	def __init__(self):
		super(GPS,self).__init__()
		self.session = gps.gps("localhost","2947")
		self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)


	def run(self):
		while self.alive:
			report = self.session.next()
			if report['class'] == 'TPV':
				if report['mode'] in (2,3):
					self.data = report
					self.publish()

	def publish(self):
		manager.publish('gps',self.data)

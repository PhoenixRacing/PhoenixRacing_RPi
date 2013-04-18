from RpiGpioObject import *
from dateutil import tz
import time, gps, datetime

class Tachometer(RpiGpioDevice):
	"""A device that uses a hall effect sensor and a magnet on
	a rotating shaft to estimate the angular speed of the shaft."""
	def __init__(self, pin):
		super(Tachometer, self).__init__({pin:IO_TYPES.INPUT})
		self.alive = True
		self.lastUpdateTime = self.lastInputTime = datetime.datetime.now()
		#self.updatePeriod = .01
		self.lastState = self.pins[0].get()
		self.averagedRPM = 0
		self.numberOfMagnets = 2
		self.alpha = .33

	def get(self):
		return self.averagedRPM

	def run(self):
		#wait for the first edge
		while self.pins[0].get() and self.alive:
			#print 'waiting for first input'
			pass

		#loop until destroyed
		while self.alive:
			now = datetime.datetime.now()
			state = self.pins[0].get()

			#an edge of the magnet
			if state is not self.lastState:
				self.lastState = state
	
				#a rising edge of the magnet
				if not state:
					dt = max(1, (now - self.lastInputTime).microseconds)/1000000.0
					rpm = 60.0 / self.numberOfMagnets / dt
					self.averagedRPM = self.averagedRPM*(1-self.alpha) + rpm*self.alpha
					self.lastInputTime = self.lastUpdateTime = now
			
			#catch the case when the input stops
			elif now - self.lastUpdateTime > datetime.timedelta(seconds=0.25):
				dt = max(1, (now - self.lastInputTime).total_seconds())
				averagedRPM = 60.0 / self.numberOfMagnets / dt
				if averagedRPM < 5:
					self.averagedRPM = 0
				else:
					self.averagedRPM = averagedRPM
				self.lastUpdateTime = now

	def stop(self):
		self.alive = False

class GPSReport(object):
	def __init__(self,reportDict):
		if (reportDict.mode == 0) or (reportDict.mode == 1):
			self.lock = False
			self.status = 'No Lock'
		else:
			self.lock = True
			if (reportDict.mode == 1):
				self.status = '2D Lock'
			elif (reportDict.mode == 2):
				self.status = '3D Lock'

			date = reportDict.time.partition('T')[0]
			time = reportDict.time.partition('T')[2].partition('.')[0]
			timedate = date + ' ' +  time
			self.time = datetime.datetime.strptime(timedate, '%Y-%m-%d %H:%M:%S')
			self.time.replace(tzinfo=tz.tzutc())
			
			#build a location
			self.latitude = reportDict.lat
			self.longitude = reportDict.lon
			self.altitude = reportDict.alt
			self.latErr = reportDict.epy
			self.lonErr = reportDict.epx
			self.altErr = reportDict.epv
	
			#TODO figure out the units
			#velocity
			self.speed = reportDict.speed
			self.speedErr = reportDict.eps
			self.heading = reportDict.track

	def getPosDecimal(self):
		return (self.latitude, self.longitude)

	def getPosDMS(self):
		if not self.lock:
			return ((None,)*3,)*2
		#latitude
		positive = self.latitude >= 0
		self.latitude = abs(self.latitude)
		latMin,latSec = divmod(self.latitude*3600,60)
		latDeg,latMin = divmod(latMin,60)
		latDeg = latDeg if positive else -latDeg
		#longitude
		positive = self.longitude >= 0
		self.longitude = abs(self.longitude)
		lonMin,lonSec = divmod(self.longitude*3600,60)
		lonDeg,lonMin = divmod(lonMin,60)
		lonDeg = lonDeg if positive else -lonDeg
		return ((latDeg,latMin,latSec), (lonDeg,lonMin,lonSec))

	def __str__(self):
		if not self.lock:
			return 'No satellite lock'

		lat, lon = self.getPosDMS()

		return 'Time:      %s \n' % (self.time.__str__(),) +\
			   'Latitude:  %d %d %f +/- %f meters\n' % (lat + (self.latErr,))+\
			   'Longitude: %d %d %f +/- %f meters\n' % (lon + (self.lonErr,))+\
			   'Altitude:  %f +/- %f \n' % (self.altitude, self.altErr)+\
			   'Speed:     %f +/- %f \n' % (self.speed, self.speedErr)+\
			   'heading:   %f' % (self.heading,)
			   

class GPS(RpiSerialDevice):
	def __init__(self):
		super(GPS, self).__init__()
		self.session = gps.gps("localhost","2947")
		self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
		self.data = None

	def run(self):
		while self.alive:
			report = self.session.next()
			if report['class'] == 'TPV':
				newReport = GPSReport(report)
				if newReport.lock:
					self.data = newReport

	def getLatLon(self):
		if self.data is None:
			return None
		return self.data.getPosDecimal

	def getTime(self):
		if self.data is None:
			return None
		return self.data.time

	def getVel(self):
		if self.data is None:
			return None
		return (self.data.speed, self.data.heading)

	def __str__(self):
		return self.data

class Dashboard(RpiSPIDevice):
	def __init__(self, tach, spedo)

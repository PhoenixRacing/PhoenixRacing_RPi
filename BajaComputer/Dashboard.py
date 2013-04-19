class Dashboard(BajaDevice):
	START_CHAR = 0x10
	END_CHAR = 0x11
	BUTTON_OFF = 0
	BUTTON_GREEN = 1
	BUTTON_RED = 2

	INDICATOR_UP = 0
	INDICATOR_DOWN = 1
	INDICATOR_YELLOW = 2
	INDICATOR_ERROR = 3
	INDICATOR_DEBUG = 4

	def __init__(self):
		self.data = {'tach':0, 'digits1':(1,1,1,1), 'decimal1':0b00000010, 'colon1':1,\
					'digits2':(1,1,1,1), 'decimal2':0b00000010, 'colon2':1,\
					'buttonLights':GREEN, 'indicators':(1,1,1,1,1)}


	def run():
		self.status = spi.openSPI(speed=200000,device="/dev/spidev0.1")
		while self.alive:
			if self.newData:
				self.newData = False
				message = (self.data['tach'],) + self.data['digits1'] + (self.data['decimal1'],) +\
				(self.data['colon1'],) + self.data['digits2'] + (self.data['decimal2'],) + (self.data['colon1'],) +\
				(self.data['buttonLights'],) + self.data[indicators]
				message = (self.START_CHAR,) + message + (self.END_CHAR,)
				for b in message:
					self.buttonState = spi.transfer((b,))
			elif self.flushButton:
				self.buttonState = spi.transfer(self.END_CHAR))
				self.flushButton = False
		spi.closeSPI()

	def updateTach(value):
		value = min(10,max(0,value))
		self.data['tach'] = value
		self.newData = True

	def updateSSD(num,ssd):
		self.data['colon'+str(num)] = ssd.colon
		self.data['decimal'+str(num)] = ssd.decimal
		self.data['digits'+str(num)] = ssd.digits
		self.newData = True

	def updateButtonLight(value):
		self.data['buttonLights'] = value
		self.newData = True

	def updateIndicators(led,value):
		temp = list(self.data['indicators'])
		temp[led] = value
		self.data['indicators'] = tuple(temp)
		self.newData = True

	def getButton():
		self.flushButton = True
		while self.flushButton:
			pass
		return self.buttonState

class SSD(object):
	def __init__(self, val = None, decimal=0, hour=None, minute=None, second = None):
		if val:
			self.colon = False
			self.decimal = int(2**(decimal-1))
			if self.decimal <= 1:
				self.decimal = 0#remove a ueseless decimal

			val *= 10**decimal
		elif hour:
			self.colon = True
			self.decimal = 0
			val = 100*hour + minute
		else:
			self.colon = True
			self.decimal = 0
			val = 100*minute + second

		digits = []
		for i in range(4):
			val, digits[i] = divmod(val, 10)
		self.digits = tuple(digits[::-1])
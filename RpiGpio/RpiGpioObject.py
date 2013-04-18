import RPi.GPIO as GPIO
import threading
import spi


"""#####"""
"""SETUP"""
"""#####"""

GPIO.setmode(GPIO.BOARD)

# allows the generation of enums
def enum(*sequential):
    return type('Enum', (), dict(zip(sequential, range(len(sequential)))))

IO_NAMES = ('INPUT', 'OUTPUT', 'SDA', 'SCL', 'GPCLK0',\
		'SERIAL_TXD', 'SERIAL_RXD', 'PCM_CLK', 'PCM_DOUT',\
		'MOSI','MISO','SCLK','CE0','CE1')
IO_TYPES = enum(*IO_NAMES)

pinList = [3,5,7,8,10,11,12,13,15,16,18,19,21,22,23,24,26]
ioTypes = [{IO_TYPES.INPUT,IO_TYPES.OUTPUT}]*len(pinList)
validPins = dict(zip(pinList,ioTypes))
validPins[3].add(IO_TYPES.SDA)
validPins[5].add(IO_TYPES.SCL)
validPins[7].add(IO_TYPES.GPCLK0)
validPins[8].add(IO_TYPES.SERIAL_TXD)
validPins[10].add(IO_TYPES.SERIAL_RXD)
validPins[12].add(IO_TYPES.PCM_CLK)
validPins[13].add(IO_TYPES.PCM_DOUT)
validPins[19].add(IO_TYPES.MOSI)
validPins[21].add(IO_TYPES.MISO)
validPins[23].add(IO_TYPES.SCLK)
validPins[24].add(IO_TYPES.CE0)
validPins[26].add(IO_TYPES.CE1)



"""##########"""
"""Exceptions"""
"""##########"""
"""
Abstract Classes
"""
class PinException(Exception):
	def __init__(self,pin):
		self.pinNum = pin

class PinIOException(PinException):
	def __init__(self,pin,ioType):
		super(PinIOException, self).__init__(pin)
		self.ioType = ioType

"""
Implementation Classes
"""
class InvalidPinException(PinException):
	def __str__(self):
		return 'Pin %d is not a valid GPIO pin' % (self.pinNum,)

class GhostPinException(PinException):
	def __str__(self):
		return 'Pin %d is not currently registered' % (self.pinNum,)

class PinConflictException(PinIOException):
	def __str__(self):
		return 'Pin %d is already setup as a(n) %s pin' % \
		(self.pinNum,IO_NAMES[self.ioType])

class InvalidPinAccessException(PinIOException):
	def __init__(self,pin,ioType,ioViolation):
		super(InvalidPinAccessException, self).__init__(pin,ioType)
		self.ioViolation = ioViolation

	def __str__(self):
		return 'Pin %d is an %s pin and you attempted to access it like an %s pin'\
		% (self.pinNum,IO_NAMES[self.ioType],IO_NAMES[self.ioViolation])

"""#######"""
"""Classes"""
"""#######"""

class RpiGpioPin(object):
	"""The wrapper for an individual pin on the RPi"""
	def __init__(self,pinNum,ioType):
		self.pinNum = pinNum
		self.ioType = ioType
		if ioType in (IO_TYPES.INPUT,):
			GPIO.setup(pinNum, GPIO.IN)
		elif ioType in (IO_TYPES.OUTPUT,):
			GPIO.setup(GPIO.OUT)

	#TODO make these methods more robust (i.e. handle all of the IO_TYPES)
	def get(self):
		if self.ioType is IO_TYPES.INPUT:
			return GPIO.input(self.pinNum)
		else:
			raise InvalidPinAccessException(self.pinNum,self.ioType,IO_TYPES.INPUT)

	def set(self,val):
		if self.ioType is IO_TYPES.OUTPUT:
			GPIO.output(self.pinNum,val)
		else:
			raise InvalidPinAccessException(self.pinNum,self.ioType,IO_TYPES.OUTPUT)


class PinManager(object):
	"""The manages the instantiation and destruction of pins"""
	
	def __init__(self):
		#this will be a dictionary that maps pin numbers to a list of a
		#RpiGpioPin object and a counter for the devices registered on the pin
		#pins -> {pinNum : [RpiGpioPin, deviceCounter]}
		self.pins = dict()

	def registerDeviceOnPin(self, pinNum, ioType):
		#test against valid pins
		if pinNum not in validPins:
			raise InvalidPinException(pinNum)

		#test for IO conflicts
		if (pinNum in self.pins) and (self.pins[pinNum].ioType is not ioType):
			raise PinConflictException(pinNum,ioType)

		#register the device
		self.pins[pinNum] = self.pins.get(pinNum,[RpiGpioPin(pinNum,ioType),0])
		self.pins[pinNum][1] += 1

		#TODO perhaps in the future all of the GPIO devices will have a device id
		#and we will actually track each of these device ids
		return self.pins[pinNum][0]

	def unregisterDeviceOnPin(self, pinNum):
		#test against instantiated pins
		if pinNum not in self.pins:
			raise GhostPinException(pinNum)

		self.pins[pinNum][1] -= 1

		#if the key is unregistered from all of its users delete it
		if self.pins[pinNum][1] == 0:
			del self.pins[pinNum]


class RpiGpioDevice(object):
	"""The parent object for all GPIO devices"""
	manager = PinManager()

	def __init__(self, pinLayout):
		self.pins = []
		self.thread = None
		self.alive = True
		for pin, ioType in pinLayout.items():
			self.pins.append(self.manager.registerDeviceOnPin(pin,ioType))

	def __call__(self):
		self.run()

	def run(self):
		raise NotImplementedError

	def start(self):
		self.thread = threading.Thread(target = self)
		self.thread.start()

	def __del__(self):
		#unregister all of the pins
		for pin in self.pins:
			self.manager.unregisterDeviceOnPin(pin.pinNum)

class RpiSerialDevice(RpiGpioDevice):
	"""A device that can communicate over the serial line"""
	#TODO implement this class (i.e. learn more about how the RPi deals with serial communication)
	#TODO it would probably be bad to have more than one device communicate over the
	#     serial line at once, so maybe there should be a static (class) lock on the
	#     write method
	def __init__(self):
		super(RpiSerialDevice, self).__init__({8:IO_TYPES.SERIAL_TXD, 10:IO_TYPES.SERIAL_RXD})
		self.alive = True;

	def run(self):
		while self.alive:
			#wait for messages to send/recieve
			raise NotImplementedError

	def stop(self):
		self.alive = False

class RpiSPIDevice(RpiGpioDevice):
	"""A device that can communicate over the SPI line"""
	#TODO actually implement this class properly
	def __init__(self, deviceNum, speed=200000, delay=150, startChar=0x10, endChar=0x11):
		if deviceNum is 0:
			pinNum = 24
			pinType = IO_TYPES.CE0
			deviceName = "/dev/spidev0.0"
		elif deviceNum is 1:
			pinNum = 26
			pinType = IO_TYPES.CE1
			deviceName = "/dev/spidev0.1"
		super(RpiSPIDevice, self).__init__({19:IO_TYPES.MOSI, 21:IO_TYPES.MISO, 23:IO_TYPES.SCLK, pinNum:pinType})
		self.status = spi.openSPI(speed=speed, device=deviceName, delay=delay)
		self.start = startChar
		self.end = endChar

	def run(self):
		while self.alive:
			#wait for messages to send/recieve
			raise NotImplementedError

	def send(self,data):
		"""data must be an iterable that returns bytes"""
		for b in data:
			spi.transfer((b,))

	def stop(self):
		self.alive = False
		spi.closeSPI()

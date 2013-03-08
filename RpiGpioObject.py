import RPi.GPIO as GPIO
from GpioExceptions import *
import threading

GPIO.setmode(GPIO.BOARD)

INPUT = True
OUTPUT = False

class RpiGpioPin(object):
	"""The wrapper for an individual pin on the RPi"""
	def __init__(self,pinNum,ioType):
		self.pinNum = pinNum
		GPIO.setup(pinNum, ioType)

	def get(self):
		if self.ioType:
			return GPIO.input(self.pinNum)
		else:
			raise InvalidPinAccessException(self.pinNum,ioType)

	def set(self,val):
		if self.ioType:
			raise InvalidPinAccessException(self.pinNum,ioType)
		else:
			GPIO.output(self.pinNum,val)



class PinManager(object):
	"""The manages the instantiation and destruction of pins"""
	validPins = {8, 10, 12, 16, 18, 22, 24, 26, 3, 5, 7, 11, 13, 15, 19, 21, 23}
	
	def __init__(self):
		self.pins = dict()

	def registerDeviceOnPin(self, pinNum, ioType):
		#test against valid pins
		if pinNum not in self.validPins:
			raise InvalidPinException(pinNum)

		#test for IO conflicts
		if (pinNum in self.pins) and (self.pins[pinNum].ioType is ioType):
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
			raise GhostPinException

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

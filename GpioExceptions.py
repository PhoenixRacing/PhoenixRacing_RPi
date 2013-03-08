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
		return 'Pin %d is not a valid GPIO pin' % (self.pin,)

class GhostPinException(PinException):
	def __str__(self):
		return 'Pin %d is not currently registered' % (self.pin,)

class PinConflictException(PinIOException):
	def __str__(self):
		return 'Pin %d is already specified as an %s pin' % \
		(self.pinNum,'input' if self.ioType else 'output')

class InvalidPinAccessException(PinIOException):
	def __str__(self):
		return 'Pin %d is an %s pin and you attempted to access it like an %s pin'\
		% (self.pinNum,) + ('input', 'output') if ioType else ('output','input')
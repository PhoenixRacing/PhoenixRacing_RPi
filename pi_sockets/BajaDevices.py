import threading, spi, math
import datetime

class ThreadObject(threading.Thread):
	"""A wrapper for the threading.Thread object"""
	def __init__(self):
		super(ThreadObject, self).__init__(target=self.run)
		self.alive = False

	def run(self):
		while self.alive is False:
			raise NotImplementedError

	def start(self):
		self.alive = True
		super(ThreadObject, self).start()

	def stop(self):
		self.alive = False

class DataManager(ThreadObject):
	def __init__(self, timer):
		super(DataManager, self).__init__()
		self.subscribers = dict();
		self.timer = timer

	def subscribe(self, msgClass, callback):
		if msgClass in self.subscribers.keys():
			self.subscribers[msgClass].append(callback)
		else:
			self.subscribers[msgClass] = [callback]

	def publish(self, msg):
		print self.subscribers
		for callback in self.subscribers.get(msg.__class__,[]):
			callback(msg)
			print 'publishing to ',callback

		print 'publishing ', msg

class BajaDevice(ThreadObject):
	pass

class Timer(object):
	"""Keeps the global time since start"""
	def start(self):
		self.startTime = datetime.datetime.now()

	def getAbsTime(self):
		"""System time"""
		return datetime.datetime.now()

	def getTime(self):
		"""Time since start"""
		return datetime.datetime.now() - self.startTime

timer = Timer()
manager = DataManager(timer)

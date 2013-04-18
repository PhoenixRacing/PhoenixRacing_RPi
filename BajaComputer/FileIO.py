from BajaDevices import *

class Talker(object):
	def __init__(self,topics):
		for topic in topics:
			manager.subscribe(topic,self.talk)

	def talk(self,topic,data):
		print topic,data['lon']

class Logger(object):
	def __init__(self,topics):
		for topic in topics:
			manager.subscribe(topic,self.log)

	def log(self, topic, data):
		pass#TODO write data to a file

def aCallback(topic, data):
	print data

manager.subscribe('gps',aCallback)
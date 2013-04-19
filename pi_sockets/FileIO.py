from BajaDevices import *
import csv, datetime, json

class Talker(object):
	def __init__(self,msgClasses, currentValues):
		for msgClass in msgClasses:
			manager.subscribe(msgClass,self.talk)

	def talk(self,msg):
		currentValues[msg.name] = msg.data
		print msg.name, msg.data

class Log(object):
	def __init__(self,aFile,aWriter):
		self.file = aFile
		self.writer = aWriter
		self.initialized = False
		self.keys = []

	def writeData(self,data):
		#TODO: not critical, but we should make event items for each post
		#so that we can have a consisten file format

		if not self.initialized:
			self.writer.writerow(sorted(data.keys()))
			self.initialized = True

		self.writer.writerow(list(val for (key, val) in sorted(data.items())))

	def close(self):
		self.file.close()


class Logger(object):
	def __init__(self, msgClasses,filePrefix="./data/"):
		self.prefix = filePrefix
		self.suffix = (str(datetime.datetime.now()).replace(' ','')).split('.')[0] + '.csv'
		self.logs = dict()
		for aClass in msgClasses:
			aFile = open(self.prefix + aClass.name + self.suffix,'a')
			aWriter = csv.writer(aFile)
			self.logs[aClass] = Log(aFile, aWriter)
			manager.subscribe(aClass,self.log)

	def log(self, msg):
		self.logs[msg.__class__].writeData(msg.data)

	def close(self):
		for log in self.logs.values():
			log.close()



#BajaSAE
#h0rsepow3r!
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen

import time
import json
import collections

import Sensors
from BajaDevices import timer
import FileIO, os
from BajaMessages import *
from Dashboard import *


from tornado.options import define, options
define("port", default=8080, help="run on the given port", type=int)
define("host", default="0.0.0.0")

clients = []

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print 'new connection'
		clients.append(self)
		self.write_message("connected")
	
	def on_message(self, message):
		print 'message received %s' % message

	def on_close(self):
		print 'connection closed'
		clients.remove(self)

def sendToClient():
	for c in clients:
		c.write_message(json.dumps(currentValues))

# main
def main():
	currentValues = collections.defaultdict(dict)

	talker = FileIO.Talker([TachometerMessage,SpeedometerMessage,GPSMessage])
	# logger = FileIO.Logger([TachometerMessage,SpeedometerMessage,GPSMessage],filePrefix = '/home/phoenix/Data/')

	timer.start()
	tach = Sensors.Tachometer(15)
	speedo = Sensors.Speedometer(16)
	aGps = Sensors.GPS()
	dash = Dashboard()

	tach.start()
	speedo.start()
	aGps.start()
	dash.start()

	# wait for initialization 
	time.sleep(1)

	app = tornado.web.Application(
		handlers=[
			(r"/", IndexHandler),
			(r"/ws", WebSocketHandler)
		]
	)

	httpServer = tornado.httpserver.HTTPServer(app)
	httpServer.listen(options.port, address=options.host)
	print "listening on port: ", options.port

	mainLoop = tornado.ioloop.IOLoop.instance()
	schedular = tornado.ioloop.PeriodicCallback(checkResults, 10, io_loop = mainLoop)
	
	try:
		schedular.start()
		mainLoop.start()
	except KeyboardInterrupt:
		tach.stop()
		speedo.stop()
		aGps.stop()
		dash.stop()
		schedular.stop()
		mainLoop.stop()

if __name__=="__main__":
	main()
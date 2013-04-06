import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from tornado.options import define, options
define("port", default=8080, help="run on the given port", type=int)
define("host", default="0.0.0.0")

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print 'new connection'
		self.write_message("connected")
	
	def on_message(self, message):
		print 'message received %s' % message
		self.write_message('message received %s' % message)

	def on_close(self):
		print 'connection closed'

if __name__=="__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application(
		handlers=[
			(r"/", IndexHandler),
			(r"/ws", WebSocketHandler)
		]
	)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port, address=options.host)
	tornado.ioloop.IOLoop.instance().start()


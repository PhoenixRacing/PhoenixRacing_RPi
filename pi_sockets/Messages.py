class Message(object):
	keys = ('test',)
	name = 'general'
	def __init__(self,data):
		self.data = dict()
		for key in self.keys:
			self.data[key] = data.get(key,None)

	def __getitem__(self,*args):
		return self.data.__getitem__(*args)

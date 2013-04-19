import Messages
class TachometerMessage(Messages.Message):
	keys = ('rpm')
	name = 'tach'

class SpeedometerMessage(Messages.Message):
	keys = ('rpm','speed')
	name = 'speedo'

class GPSMessage(Messages.Message):
	keys = ('lat','lon','alt','speed','heading','climb','latErr','lonErr','altErr','speedErr')
	name = 'gps'
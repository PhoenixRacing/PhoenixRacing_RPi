import gps
from datetime import datetime
from dateutil import tz

# Set up time zones
from_zone = tz.tzutc()
to_zone   = tz.tzlocal()

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

while True:
	try:
		report = session.next()
		# Wait for a 'TPV' report and display the current time
		# To see all report data, uncomment the line below
		#print report
		if report['class'] == 'TPV':
			if hasattr(report, 'time'):
				date = report.time.partition('T')[0]
				time = report.time.partition('T')[2].partition('.')[0]
				timedate = date + ' ' +  time
				utc = datetime.strptime(timedate, '%Y-%m-%d %H:%M:%S')
				utc = utc.replace(tzinfo=from_zone)
				localtime = utc.astimezone(to_zone)
				print 'time:      ' , localtime
			if hasattr(report, 'lat'):
				print 'latitude:  ' , report.lat
			if hasattr(report, 'lon'):
				print 'longitude: ' , report.lon
			if hasattr(report, 'alt'):
				print 'altitude:  ' , report.alt
			if hasattr(report, 'speed'):
				print 'speed:     ' , report.speed
	except KeyError:
		pass
	except KeyboardInterrupt:
		quit()
	except StopIteration:
		session = None
		print "GPSD has terminated"

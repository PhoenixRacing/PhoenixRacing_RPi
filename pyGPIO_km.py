from __future__ import division
import RPi.GPIO as GPIO
import datetime
import csv

#setup the board layout
SPEDO_PIN = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SPEDO_PIN, GPIO.IN)

#initialize variables
state = GPIO.input(SPEDO_PIN)
firstTime = lastUpdate = last = datetime.datetime.now()
numberOfMagnets = 2
rpm = averagedRPM = 0
alpha = .33 #filter constant

#setup csv stuff
dataFile = open('eggs.csv','a')
dataWriter = csv.writer(dataFile)
initMsg = 'Starting Test %d/%d/%d %d:%d:%2f' % (firstTime.day, firstTime.month, firstTime.year, firstTime.hour, firstTime.minute, firstTime.second+firstTime.microsecond/1000000.0)
dataWriter.writerow([initMsg])
dataWriter.writerow(['Spedometer','Tachometer','Time since start'])

#main loop
while True:
    try:
        now = datetime.datetime.now()
        #an edge of the magnet
        if GPIO.input(SPEDO_PIN) is not state:
            state = not state

            #a leading edge of the magnet
            if GPIO.input(SPEDO_PIN) is False:
                dt = max(1, (now - last).microseconds)/1000000.0
                rpm = 60.0 / numberOfMagnets / dt
                averagedRPM = averagedRPM*(1-alpha) + rpm*alpha
                last = now
    
        #catch the case when the input stops
        elif now - last > datetime.timedelta(seconds=0.25):
            print 'too slow'
            averagedRPM = max(1e-4,(averagedRPM * 2) / 3)
            last = now
        
        #print and log data
        if now - lastUpdate > datetime.timedelta(seconds=0.5):
            print averagedRPM
            dataWriter.writerow([averagedRPM,averagedRPM,round((now-firstTime).total_seconds(),1)])
            lastUpdate = now
            
    except (KeyboardInterrupt,SystemExit):
        print 'Shutting down...'
        dataFile.close()
        break

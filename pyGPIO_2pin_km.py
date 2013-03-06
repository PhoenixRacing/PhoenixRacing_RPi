from __future__ import division
import RPi.GPIO as GPIO
import datetime
import csv

#setup the board layout
SPEDO_PIN = 11
TACH_PIN = 13

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SPEDO_PIN, GPIO.IN)
GPIO.setup(TACH_PIN, GPIO.IN)

#initialize variables
spedo_state = GPIO.input(SPEDO_PIN)
tach_state = GPIO.input(TACH_PIN)
firstTime = lastUpdate = last = datetime.datetime.now()
numberOfMagnets_spedo = numberOfMagnets_tach = 2
rpm_spedo = rpm_tach = averagedRPM_spedo = averagedRPM_tach = 0
alpha = .33 #filter constant

#setup csv stuff
dataFile = open('First_CVT_Test.csv','a')
dataWriter = csv.writer(dataFile)
initMsg = 'Starting Test %d/%d/%d %d:%d:%2f' % (firstTime.day, firstTime.month, firstTime.year, firstTime.hour, firstTime.minute, firstTime.second+firstTime.microsecond/1000000.0)
dataWriter.writerow([initMsg])
dataWriter.writerow(['Spedometer','Tachometer','Time since start'])

#main loop
while True:
    try:
        now = datetime.datetime.now()
        
        #SPEDO
        #an edge of the magnet
        if GPIO.input(SPEDO_PIN) is not spedo_state:
            spedo_state = not spedo_state

            #a leading edge of the magnet
            if GPIO.input(SPEDO_PIN) is False:
                dt = max(1, (now - last).microseconds)/1000000.0
                rpm_spedo = 60.0 / numberOfMagnets_spedo / dt
                averagedRPM_spedo = averagedRPM_spedo*(1-alpha) + rpm_spedo*alpha
                last = now
    
        #catch the case when the input stops
        elif now - last > datetime.timedelta(seconds=0.25):
            print 'too slow'
            averagedRPM_spedo = max(1e-4,(averagedRPM_spedo * 2) / 3)
            last = now

        #TACH
        #an edge of the magnet
        if GPIO.input(TACH_PIN) is not tach_state:
            tach_state = not tach_state

            #a leading edge of the magnet
            if GPIO.input(TACH_PIN) is False:
                dt = max(1, (now - last).microseconds)/1000000.0
                rpm_tach = 60.0 / numberOfMagnets_tach / dt
                averagedRPM_tach = averagedRPM_tach*(1-alpha) + rpm_tach*alpha
                last = now
    
        #catch the case when the input stops
        elif now - last > datetime.timedelta(seconds=0.25):
            print 'too slow'
            averagedRPM_tach = max(1e-4,(averagedRPM_tach * 2) / 3)
            last = now

        #print and log data
        if now - lastUpdate > datetime.timedelta(seconds=0.5):
            print "Spedo: %3f Tach: %3f" % (averagedRPM_spedo, averagedRPM_tach)
            dataWriter.writerow([averagedRPM_spedo,averagedRPM_tach,round((now-firstTime).total_seconds(),1)])
            lastUpdate = now
            
    except (KeyboardInterrupt,SystemExit):
        print 'Shutting down...'
        dataFile.close()
        break

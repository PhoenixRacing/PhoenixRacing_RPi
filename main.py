from BajaSensors import *
import time
import csv

# CSV stuff
f_name = "./cvt_test/CVT_Test_" + str(datetime.datetime.now()) + ".csv"
dataFile = open(f_name,'w+')
dataWriter = csv.writer(dataFile)
firstTime = datetime.datetime.now()
initMsg = 'Starting Test %d/%d/%d %d:%d:%2f' % (firstTime.day, firstTime.month, firstTime.year, firstTime.hour, firstTime.minute, firstTime.second+firstTime.microsecond/1000000.0)
dataWriter.writerow([initMsg])

tach = Tachometer(22)
speedo = Tachometer(18)

tach.start()
speedo.start()

while True:
  try:
    time.sleep(1)
    print "Speedo: %f  Tach: %f" % (tach.get()[0], speedo.get()[0])
    dataWriter.writerow([speedo.get()[0],tach.get()[0], tach.get()[1]])

  except KeyboardInterrupt, SystemExit:
    print 'Shutting down...'
    tach.stop()
    speedo.stop()

    # close csv file
    dataWriter.writerow([])
    dataFile.close()

    #create plot png
    import cvt_test_mod as CVT
    fig = CVT.save_plot(f_name)
    break

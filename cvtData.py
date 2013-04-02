import csv
import datetime
import itertools
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline


class testData (object):
	def __init__(self, dateTime, speedo, tach, timeStamp):
		self.dateTime = dateTime
		self.speedo = speedo
		self.tach = tach
		self.timeStamp = timeStamp

	def __str__(self):
		return 'Date: ' + str(self.dateTime) + '\nSpeedo: ' + len(self.speedo) + '\nTach: ' + len(self.tach)

class cvtData (object):
	def __init__(self):
		self.tests = {}

	def addTestData(self, tests):
		for test in tests:
			dateList = test[0][0].split()
			date = dateList[-2].split('/')
			time = dateList[-1].split(':')
			DT = datetime.datetime(int(date[2]), int(date[1]), int(date[0]), int(time[0]), int(time[1]), int(float(time[2])))
			del test[0]
			data = zip(*test)
			self.tests[DT] = testData(DT, np.array(map(float, data[0])), np.array(map(float, data[1])), np.array(map(float, data[2])))


def get_tests_csv(filename):
	test = []
	c = csv.reader(open(filename))
	groups = itertools.groupby(c, lambda line: line==[])
	for is_seperator, rawdata in groups:
		if not is_seperator:
			test.append(list(rawdata))
	return test

def plotCVTData(cvt, test_no = 0):
	t = cvt.tests.values()[test_no]
	tnew = np.linspace(t.tach.min(), t.tach.max(), len(t.speedo))
	smooth = spline(t.tach, t.speedo, tnew)

	plt.plot(t.tach, t.speedo)
	plt.show()

	# j = 0
	# i = len(cvt.tests.values())
	# for k,v in cvt.tests.iteritems():
	# 	plt.subplot(i, 1, j)
	# 	j += 1
	# 	plt.plot(v.speedo, v.tach)
	# 	plt.ylabel('RPM')
	# 	plt.xlabel('Speed')
	# 	plt.title(str(k))

def main():
	tests = get_tests_csv(sys.argv[1])
	cvt = cvtData()
	cvt.addTestData(tests)
	plotCVTData(cvt)

main()
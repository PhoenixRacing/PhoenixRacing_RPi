import csv
import datetime
import itertools
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# from scipy.interpolate import spline


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

def plotCVTData(cvt):
	t = cvt.tests.values()[0]
	# tnew = np.linspace(t.speedo.min(), t.speedo.max(), len(t.speedo))
	# smooth = spline(t.speedo, t.tacho, tnew)

	plt.plot(t.speedo, t.tach, 'ro-')
	plt.ylabel('RPM')
	plt.xlabel('Speed')

	plt.title(str(t.dateTime))

	plt.xlim(xmin=0)
	plt.ylim(ymin=0)
	plt.savefig(str(t.dateTime)+'.png', bbox_inches=0)
	return str(t.dateTime)+'.png'

def save_plot(results_file):
	tests = get_tests_csv(results_file)
	cvt = cvtData()
	cvt.addTestData(tests)
	fig = plotCVTData(cvt)
	return fig
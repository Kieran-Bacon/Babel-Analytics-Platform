from os import listdir 
from os.path import join
import time

class Logger:

	def __init__(self):

		self.store = "./logs"

	def getAnalytics(self, srv_id = 0, resource="", timeframe = 0 ):
		# Initialise all variables.
		reqtTotal = 0
		genTotal = 0
		minTime = 0
		avgTime = 0
		maxTime = 0
		errTotal = 0
		filepaths = []
		timepaths = []
		if( timeframe != 0 ):
			timepaths = times( time.strftime("%d-%m-%Y"), timeframe )
			timepaths += [time.strftime("%d-%m-%Y")]

		# Find all log files to inspect.
		if srv_id == 0:
			dirs = listdir( self.store )
			for dir in dirs:
				filepaths += [join( self.store, dir, f ) for f in listdir( join( self.store, dir ) )]
		else:
			filepaths = [join( self.store, str(srv_id), f) for f in listdir( join(self.store, str(srv_id)) )]

		# For each file open it up for viewing.
		for file in filepaths:
			if( len(timepaths) != 0 and file.split('/')[-1:][0] not in timepaths ):
				continue
			with open( file, "r" ) as stream:
				for line in stream:
					parts = line.split( ' ' )
					if (parts[0] == "ANALYTICS" and resource == "") or (parts[0] == "ANALYTICS" and parts[2] == resource):
						parts[3] = float(parts[3])
						parts[4] = int(parts[4])
						parts[5] = int(parts[5])
						reqtTotal += 1
						genTotal += parts[4]

						if parts[3] < minTime or minTime == 0:
							minTime = parts[3]
						avgTime += parts[3]
						if parts[3] > maxTime:
							maxTime = parts[3]
					
						if parts[5] != 200:
							errTotal += 1
		if reqtTotal:
			avgTime = avgTime/reqtTotal
		return( reqtTotal, genTotal, round(minTime), round(avgTime), round(maxTime), errTotal )

	def getTimedAnalytics(self, srv_id, timeframe, resource = "" ):
		timepaths = times( time.strftime("%d-%m-%Y"), timeframe )
		timepaths += [time.strftime("%d-%m-%Y")]
		filepaths = [join( self.store, str(srv_id), f) for f in listdir( join(self.store, str(srv_id)) )]

		timeplot = []
		for date in timepaths:

			reqtTotal = 0
			genTotal = 0
			minTime = 0
			avgTime = 0
			maxTime = 0
			errTotal = 0

			datePath = join( self.store, str(srv_id), date )
			if datePath in filepaths:
				with open( datePath, "r" ) as stream:
					for line in stream:
						parts = line.split( ' ' )
						if (parts[0] == "ANALYTICS" and resource == "") or (parts[0] == "ANALYTICS" and parts[2] == resource):
							parts[3] = float(parts[3])
							parts[4] = int(parts[4])
							parts[5] = int(parts[5])
							reqtTotal += 1
							genTotal += parts[4]

							if parts[3] < minTime or minTime == 0:
								minTime = parts[3]
							avgTime += parts[3]
							if parts[3] > maxTime:
								maxTime = parts[3]
						
							if parts[5] != 200:
								errTotal += 1

				if reqtTotal:
					avgTime = avgTime/reqtTotal
				timeplot.append( ( reqtTotal, genTotal, round(minTime), round(avgTime), round(maxTime), errTotal ) )
			else:
				timeplot.append( ( 0, 0, 0, 0, 0, 0) )
		return timeplot

def round( time ):
	return float(int((int( time*100000 ) + 5)/10))/10000

def times( current, numberBack ):
	numDays = [31,28,31,30,31,30,31,31,30,31,30,31]
	dmy = [int(x) for x in current.split( '-' )]

	dates = []
	for i in range( numberBack ):
		dmy[0] -= 1
		if dmy[0] == 0:
			dmy[1] -= 1
			if dmy[1] == 0:
				dmy[2] -= 1
				dmy[1] = 12
			dmy[0] = numDays[dmy[1]-1]

		string = str(dmy[0]) + '-' + str(dmy[1]) + '-' + str(dmy[2])
		dates.append( string )

	return dates[::-1]
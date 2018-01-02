import web
import hashlib
import datetime
from logger import Logger
import HelperFunctions as help
from DatabaseHandler import DatabaseHandler as db

render = web.template.render('templates')

class Dashboard:
	def GET(self):
		help.check_access()
		log = Logger()

		# Counts the number of services and the number of servers known to the Management Console.
		counts = db().executeLiteral( "SELECT (SELECT count(*) FROM services), (SELECT count(*) FROM servers)",[])[0]
		analytics = log.getAnalytics()
		tiles = [analytics[0],analytics[3],analytics[1],counts[0],counts[1],analytics[5]]

		data = db().execute( "Dashboard", 0, [])

		developing = []
		for row in data:
			percentage = (row[2]*100)/row[3]
			temp = [row[0],help.strVersion(row[1]),percentage, row[4]]
			developing.append( temp )

		#ENVIRONMENTS
		envinfo = db().execute( "Dashboard", 1, [])

		environments = []

		for env in envinfo:

			machines = db().executeLiteral( "SELECT srv_id FROM servers WHERE eid = ?", [env[0]])
			envServices = db().execute( "Dashboard", 3, [env[0]])

			if len(machines) == 0 or len(envServices) == 0:
				continue

			processedServices = []
			for ser in envServices[:5]:
				processedServices.append( [ ser[0], ser[1], help.strVersion(ser[2]), ser[3] ] )

			reqtCount = 0
			for server in machines:
				server = server[0]
				reqtCount += log.getAnalytics( server )[0]

			temp = [env[1],env[2], reqtCount, len(machines), processedServices, env[0]]
			environments.append( temp )

		print developing
		print environments
		

		return help.renderPage( "Dashboard", render.dashboard( tiles, developing, environments ))

class AJAX_dashboard:
	def POST(self):

		input = web.input( resource=-1 )

		if input.resource == -1:
			raise web.BadRequest()

		log = Logger()

		if input.resource == "pie":

			serviceNames = db().executeLiteral( "SELECT ser.service_name, ser.resource_name, env.eid FROM services ser, services_versions sv, environments env, service_deployment_lkp sdl WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = env.eid AND env.env_type = ?", ["LIVE"])
			if( len(serviceNames) == 0):
				return

			pieLegend = "["
			pieData = "["
			for ser in serviceNames:
				pieLegend += '"' + ser[0] + '", ' 

				count = 0
				servers = db().executeLiteral( "SELECT srv_id FROM servers WHERE servers.eid = ?", [ser[2]])
				for s in servers:
					results = log.getAnalytics( s[0], ser[1] )
					count += results[0]

				pieData += str( count ) + ', '

			pieLegend = pieLegend[:-2]
			pieData = pieData[:-2]
			pieLegend += "]"
			pieData += "]"
			pieChart = '{ "legend" : ' + pieLegend + ', "data" : ' + pieData + '}'

			return pieChart

		elif input.resource  == "line":

			# Constructed the general line legend.
			legend = "["
			Days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
			today = datetime.datetime.today().weekday()
			Days = Days[today+1:] + Days[:today+1]
			for day in Days:
				legend += '"' + day + '",'
			legend = legend[:-1] + "]"

			# Constuct the Environments list.
			envinfo = db().execute( "Dashboard", 1, [])

			environments = "["
			for env in envinfo:
				machines = db().executeLiteral( "SELECT srv_id FROM servers WHERE eid = ?", [env[0]])
				envServices = db().execute( "Dashboard", 3, [env[0]])

				if len(machines) == 0 or len(envServices) == 0:
					continue
				serviceNames = '['
				servicesReqt = '['
				for service in envServices:
					serviceNames += '"' + service[1] + '",'


					reqtCount = [0]*7
					for server in machines:
						resp = log.getTimedAnalytics( server[0], 7, resource=service[1] )
						for d in range(7):
							reqtCount[d] += resp[d][0]

					reqtString = '['
					for value in reqtCount:
						reqtString += str(value) + ','
					reqtString = reqtString[:-1] + ']'

					servicesReqt += reqtString + ','

				serviceNames = serviceNames[:-1] + ']'
				servicesReqt = servicesReqt[:-1] + ']'


				output  = '{ "eid":' + str(env[0]) + ','
				output += '  "name":"' + str(env[1]) + '",'
				output += '  "servicesNames":' + serviceNames + ','
				output += '  "servicesReqt": ' + servicesReqt + '}' 

				environments += output + ','
			environments = environments[:-1] + ']'
			if( environments == ']'):
				return

			return '{"legend":' + legend + ', "environments":' + environments + '}'
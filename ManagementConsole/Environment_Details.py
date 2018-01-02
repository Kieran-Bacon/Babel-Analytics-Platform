import web
import json
from logger import Logger
from DatabaseHandler import DatabaseHandler as db
import HelperFunctions as help

#to delete
from random import randint

render = web.template.render('templates')

class Environment_Details:
	def GET( self, eid ):

		help.check_access()

		env = db().executeLiteral( "SELECT eid, name, description, env_type FROM environments WHERE eid = ?", [eid] )[0]
		services = db().executeLiteral( "SELECT sv.sid, ser.service_name, sv.version, sdl.status FROM service_deployment_lkp sdl, services_versions sv, services ser WHERE sdl.eid = ? AND sdl.sid = sv.sid AND sv.sgid = ser.sgid GROUP BY ser.sgid ORDER BY version DESC" , [eid])
		servers = db().executeLiteral( "SELECT srv_id, display_name FROM servers WHERE eid = ?", [eid])

		logs = Logger()
		serversInfo = []
		for server in servers:
			results = logs.getAnalytics( srv_id=server[0] )

			serversInfo.append( list(server) + list(results) )

		return help.renderPage( "Environment Details", render.environment_details( env, services, serversInfo ) )

class AJAX_Service_Requests:
	def GET(self, eid):

		# TODO get format from somewhere

		help.check_access()

		services = db().execute( "Environment_Details", 0, [eid])

		page_info = {'xAxis': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
		version_requests = {}
		for ser in services:

			data = [ randint(0,100) for x in range(7) ]

			if ser[0] in version_requests:
				version_requests[ ser[0] ] = [ x + y for x,y in zip( version_requests[ser[0]], data )]
			else:
				version_requests[ ser[0] ] = data

		page_info["services"] = version_requests

		return json.dumps(page_info)

class AJAX_Service_CPU:

	def GET(self, eid ):

		help.check_access()

		services = db().execute( "Environment_Details", 0, [eid]) 

		data = []
		for ser in services:
			web.debug( ser[1] )
			temp = { 'label': ser[0], 'value': randint(0,100) }
			data.append( temp ) 

		jobject = { 'data': data }

		return json.dumps( jobject )
		
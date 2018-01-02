import web
import sqlite3
import HelperFunctions as help
from DatabaseHandler import DatabaseHandler  as db

render = web.template.render('templates')

class Manage_Services:
	def GET(self):
		help.check_access()

		GroupInfo = db().execute( "Services_Manage", 0, [])

		Services = []
		for service in GroupInfo:

			GroupVersions = db().executeLiteral( "SELECT sid, version FROM services_versions WHERE sgid =  ?", [service[0]] )
			values = []
			for version in GroupVersions:
				length = db().executeLiteral( "SELECT p.length FROM services ser, paths p WHERE ser.sgid = ? AND ser.pid = p.pid", [service[0]])[0][0]
				count = db().executeLiteral( "SELECT count(*) FROM services_versions sv, service_deployment_lkp sdl WHERE sv.sid = ? AND sv.sid = sdl.sid", [version[0]])[0][0]

				if count == 0:
					values.append( [version[1], 0] )
				else:
					(count*100)/length
					values.append( [version[1], (count*100)/length ] )

			Services.append([ service[2], service[3], values, service[0] ])

		return help.renderPage( 'Manage Services', render.manage_services( Services ) )
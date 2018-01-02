import web
from os.path import join
from os import remove, rmdir
import HelperFunctions as help
from AnalyticsServerInterface import Server, findPaths
from DatabaseHandler import DatabaseHandler as db

render = web.template.render('templates')

class Promote:
	def POST(self, sid):
		help.check_access()

		# Locate where the service is currently
		serviceInfo = db().executeLiteral( "SELECT ser.*, sv.* FROM services ser, services_versions sv WHERE ser.sgid = sv.sgid AND sv.sid = ?", [sid] )[0]
		sgid, pid, name, resource, version = serviceInfo[0], serviceInfo[1], serviceInfo[2], serviceInfo[3], serviceInfo[7]
		position = db().executeLiteral( "SELECT epl.position FROM services_versions sv, service_deployment_lkp sdl, env_path_lkp epl WHERE sv.sid = ? AND sv.sid = sdl.sid AND sdl.eid = epl.eid GROUP BY sv.sid ORDER BY epl.position DESC", [sid])
		if len( position ) == 0:
			position = 0
		else:
			position = position[0][0]

		# Locate the environment for the service to be deployed too.
		next = db().executeLiteral( "SELECT eid FROM env_path_lkp WHERE pid = ? AND position = ?", [pid, position + 1] )
		if len( next ) == 0:
			help.append_user_alerts( "warning", "Already at the top!", "The service version is already on the final environment of its path.")
			raise web.seeother( "/service_details_" + str(sid) )
		else:
			next = next[0][0]

		# Decide if the service should be put onto the environment.
		top = db().executeLiteral( "SELECT sv.version FROM services_versions sv, service_deployment_lkp sdl WHERE sv.sgid = ? AND sv.sid = sdl.sid AND sdl.eid = ? GROUP BY sv.sgid ORDER BY sv.version DESC", [sgid, next] )
		if len( top ) == 0:
			top = 0
		else:
			top = top[0][0]

		count = 1
		if not top > version:

			msgHeaders = { "Username": web.ctx.session.username, "Access-Token": web.ctx.session.access_token }

			envServers = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password, display_name FROM servers WHERE eid = ?", [next] )

			if top != 0:
				for server in envServers:
					Server( server[0], server[1] ).send( "DELETE", resource, msgHeaders )

			if serviceInfo[12] != "NULL" or serviceInfo[12] != '':
				status = 303
				html = serviceInfo[12]
			else:
				status = 200
				html = serviceInfo[11]
			data = {
				"name": name,
				"resource": resource,
				"status": "ACTIVE",
				"version": version,
				"mainScript": serviceInfo[10],
				"language": serviceInfo[9],
				"poolSize": serviceInfo[8],
				"HTTP_Status": status, 
				"HTML": html 
			}

			location = join( "./services", str( sgid ), str( version ) )

			count = len( envServers )
			for server in envServers:
				resp = Server( server[0], server[1] ).createService( msgHeaders, server[2], server[3], location, data )

				if resp == -1:
					help.append_user_alerts( "warning", "No Connection", "Could not form a connection with " + server[4] + ", Service not deployed.")
					count -= 1
				elif resp[0] != "200":
					help.append_user_alerts( "warning","Server rejected service!", "The server rejected the service with reason: " + resp[1] )
					count -= 1

		if count > 0:
			db().executeLiteral( "INSERT INTO service_deployment_lkp VALUES ( ?,?,? )", [next, sid, "ACTIVE"])
			help.append_user_alerts( 'info', 'Promoted ' + name + ' successfully','The service has not been deployed to all servers of the target environment')
		else:
			help.append_user_alerts( "warning", "Failed to deploy", "Through connection issues or rejections, the service has failed to be promoted.")

		raise web.seeother( "/service_details_" + str( sgid ) )

class Demote:
	def POST(self, sid):

		sgid, resource, version = db().executeLiteral( "SELECT ser.sgid, ser.resource_name, sv.version FROM services ser, services_versions sv WHERE ser.sgid = sv.sgid AND sv.sid = ?", [sid] )[0]
		eid = db().executeLiteral( "SELECT sdl.eid FROM service_deployment_lkp sdl, env_path_lkp epl WHERE sdl.sid = ? AND sdl.eid = epl.eid ORDER BY epl.position DESC", [sid] )
		if len( eid ) != 0:
			# Service on environments
			eid = eid[0][0]
			versions = db().executeLiteral( "SELECT ser.sgid, ser.service_name, ser.resource_name, sv.version, sv.main_script, sv.language, sv.poolsize, sv.get_html_file, sv.get_redirect FROM services ser, services_versions sv, service_deployment_lkp sdl WHERE ser.sgid = ? AND ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = ? ORDER BY sv.version DESC", [sgid, eid])
			runningVersion = versions[0][3];
			count = 1
			if version == runningVersion:
				msgHeaders = {"Username": web.ctx.session.username, "Access-Token": web.ctx.session.access_token }
				servers = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password, display_name FROM servers WHERE eid = ?", [eid] )

				for server in servers:
				 	Server( server[0], server[1] ).send( "DELETE", resource, msgHeaders )

				if len( versions) > 1: 
					old = versions[1]

					if old[7] == "NULL" or (old[8] != "NULL" and old[8] != ""):
						status = 303
						html = old[8]
					else:
						status = 200
						html = old[7]
					data = { 
						"name": old[1],
						"resource": old[2],
						"status": "ACTIVE",
						"version": old[3],
						"mainScript": old[4],
						"language": old[5],
						"poolSize": old[6],
						"HTTP_Status": status, 
						"HTML": html 
					}

					location = join( "./services", str( sgid ), str( old[3] ) )

					count = len( servers )
					for server in servers:
						resp = Server( server[0], server[1]).createService( msgHeaders, server[2], server[3], location, data )

						if resp == -1:
							help.append_user_alerts( "warning", "Unable to make Connection!", "A connection to the server " + server[4] + " could not be made! Service not installed." )
							count -= 1
						elif resp[0] != "200":
							help.append_user_alerts( "warning", "Server rejected new version", server[4] + " has rejected the installation of the service. Reason being: " + resp[1] )
							count -= 1


			db().executeLiteral( "DELETE FROM service_deployment_lkp WHERE sid = ? AND eid = ?", [sid, eid] )

			if count > 0:
				help.append_user_alerts( "info", "Successfully Demoted Service", "The service was Successfully demoted from it's current position" )
				raise web.seeother( "service_details_" + str( sgid ) )
			else:
				help.append_user_alerts( "warning", "Demoted Service but...", "The service was Successfully demoted but the server was unable to rollback to the previous version." )
				raise web.seeother( "service_details_" + str( sgid ) )
		else:
			# Service not on environments
			clearDir( join( "./services", str( sgid ), str( version ) ) )
			db().executeLiteral( "DELETE FROM services_versions WHERE sid = ?", [sid] )
			help.append_user_alerts( "info", "Version Deleted Entirely", "The service has been demoted from existance." )
			raise web.seeother( "service_details_" + str( sgid ))

def clearDir( dir ):
	dirs, paths = findPaths( dir )
	for file in paths:
		remove( file )
	for folder in dirs[::-1]:
		rmdir ( folder )
	rmdir( dir ) 
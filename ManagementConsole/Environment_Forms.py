import web
from os.path import join
import HelperFunctions as help
from AnalyticsServerInterface import Server
from DatabaseHandler import DatabaseHandler as db

render = web.template.render('templates')

class Add_Environment:
	
	def GET( self ):
		help.check_access()
		return help.renderPage("Add Environment", render.environment_form( 0, env_types(), free_servers(), [], [] ))

	def POST( self ):
		help.check_access()

		input = web.input( name="NULL", type="NULL", servers=[] )

		if input.name == "NULL" or input.type == "NULL":
			help.append_user_alerts( "warning", "Invalid Entry", "The information you have input is invalid")
			return help.renderPage("Add Environment", render.environment_form( 0, env_types(), free_servers(), input.servers, [input.name, input.desc, input.type] ))

		# Add Environment into the database
		eid = db().executeID( "Environment_Forms", 0, [input.name, input.desc, input.type] )

		for server in input.servers:
			db().execute( "Environment_Forms", 1, [eid, server] )
		
		help.append_user_alerts( "info", "Successfully Added", "An environment definition has been successfully added")
		raise web.seeother( "environments.html" ) 

class Edit_Environment:

	def GET( self, eid ):
		help.check_access()
		content = db().execute( "Environment_Forms", 2, [eid] )[0]
		return help.renderPage("Edit Environment", render.environment_form( eid,  env_types(), free_servers( eid ), selected_servers(eid), content ))

	def POST( self, eid ):
		help.check_access()
		input = web.input( name="NULL", type="NULL", servers=[] )

		inputServers = [ int(x) for x in input.servers]

		if input.name == "NULL" or input.type == "NULL":
			help.append_user_alerts( "warning", "Invalid Entry", "The information you have input is invalid")
			return help.renderPage("Add Environment", render.environment_form( eid, env_types(), free_servers( eid ), selected_servers(eid), [input.name, input.desc, input.type] ))

		# Ensure Paths are not affected.
		content = db().execute( "Environment_Forms", 2, [eid] )[0]
		if( content[2] != input.type ):
			pathMembership = db().executeLiteral( "SELECT * FROM env_path_lkp WHERE eid = ?", [eid] )
			if ( len( pathMembership) != 0 ):
				help.append_user_alerts( "warning", "Cannot Perform Action", "The Environment is apart of a development path and therefore cannot have its type changed. Please decouple it before trying again.")
				return help.renderPage("Add Environment", render.environment_form( eid, env_types(), free_servers( eid ), selected_servers(eid), [input.name, input.desc, input.type] ))

		# Change servers if need be.

		services = db().executeLiteral( "SELECT sv.sid, ser.service_name, ser.resource_name, sv.version, sv.main_script, sv.language, sv.poolsize, sv.get_html_file, sv.get_redirect FROM services ser, services_versions sv, service_deployment_lkp sdl WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = ? GROUP BY ser.sgid ORDER BY sv.version DESC", [eid] )
		current = [x[0] for x in db().executeLiteral( "SELECT srv_id FROM servers WHERE eid = ?", [eid])]
		removed = [x for x in current if x not in inputServers]
		added = [x for x in inputServers if x not in current ]

		print( removed, current, added )

		if len( removed ) + len( added ) > 0:
			usr = (web.ctx.session).username
			token = (web.ctx.session).access_token
			msgHeaders = { "Username": usr, "Access-Token":token}

		for srv_id in removed:
			info = db().executeLiteral( "SELECT machine_address, m_port_num, display_name FROM servers WHERE srv_id = ?", [srv_id] )[0]
			for each in services:
				resp = Server( info[0], info[1] ).send( "DELETE", each[2], msgHeaders )
				if( resp == -1 ):
					help.append_user_alert( "warning", "Connection Error", "Unable to access " + info[2] + " to remove environment services")
			db().executeLiteral( "UPDATE servers SET eid = 0 WHERE srv_id = ?", [srv_id])

		for srv_id in added:

			info = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password, display_name FROM servers WHERE srv_id = ?", [srv_id] )[0]

			print "GOT HERE"
			count = len( services )
			for service in services:
				print( service[7], service[8] )
				if service[7] == "NULL":
					status = 302
					HTML = service[8]
				else:
					status = 200
					HTML = service[7]
				data =  {
					"name": service[1],
					"resource": service[2],
					"status":"ACTIVE",
					"version": service[3], 
					"mainScript":service[4], 
					"language":service[5], 
				    "poolSize":service[6], 
				    "HTTP_Status":status, 
				    "HTML": HTML 
				}

				location = join( "./services", str(service[0]), str(service[3]) )

				resp = Server( info[0], info[1] ).createService( msgHeaders, info[2], info[3], location, data )
				print( resp )
				if resp == -1:
					help.append_user_alerts( "warning", "Couldn't Connect!", "Could not connect to " + info[4] + "!" )
					count -= 1
					break
				elif resp[0] != "200":
					help.append_user_alerts( "warning", "Server Rejected Service", info[4] + " rejected " + service[1] + " for reason: " + resp[1] )
					count -= 1

			if count > 0 or len( services ) == 0:
				# Ensure we are not changing servers that are already on an environment
				db().executeLiteral( "UPDATE servers SET eid = ? WHERE eid = 0 AND srv_id = ?",[eid, srv_id])
			else:
				help.append_user_alerts( "danger", "Server not added!", "The server has rejected all the services and therefore is not apart of the environment.")
		
		# Change database row
		db().execute( "Environment_Forms", 3, [input.name, input.desc, input.type, eid])

		# return
		help.append_user_alerts( "info", "Successfully Updated", "The information has been updated in the database.")
		raise web.seeother( "environment_details_" + eid )

class Delete_Environment:
	def GET( self, eid ):
		help.check_access()
		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}

		

		# Decouples Servers.
		Services = db().executeLiteral( "SELECT ser.resource_name FROM services ser, services_versions sv, service_deployment_lkp sdl WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = ? GROUP BY ser.sgid ORDER BY sv.version DESC", [eid])
		Servers = db().executeLiteral( "SELECT machine_address, m_port_num, display_name FROM servers WHERE eid = ?", [eid] )

		if len( Services ) > 0:
			for server in Servers:
				interface = Server( server[0], server[1] )
				for service in Services:
					resp = interface.send( "DELETE", service[0], msgHeaders )
					if resp == "FAILED":
						help.append_user_alerts( "warning", "Communication Failed", "Could not connect with " + server[3] + ", services may still be running on this machine." )

		db().execute( "Environment_Forms", 7, [eid] )

		# Deletes from Environments the env.
		db().execute( "Environment_Forms", 6, [eid] )

		# Decouples Services.
		db().executeLiteral( "DELETE FROM service_deployment_lkp WHERE eid = ?", [eid] )

		# Decouples Paths.
		paths = db().executeLiteral( "SELECT p.pid, p.length, plkp.position FROM paths p, env_path_lkp plkp WHERE eid = ?", [eid] )
		print( len( paths ) )
		for path in paths:
			print( "GET to path change" )
			# Shorten the length of the path
			db().executeLiteral( "UPDATE paths SET length = ? WHERE pid = ?", [int(path[1])-1, path[0]])
			affected = db().executeLiteral( "SELECT * FROM env_path_lkp WHERE pid = ? and position > ?", [ path[0], path[2] ])
			print( len( affected ) )
			for p in affected:

				db().executeLiteral( "UPDATE env_path_lkp SET position = ? WHERE pid = ? and eid = ?", [ int(p[2])-1, p[0], p[1] ])

		help.append_user_alerts( "info", "Successfully Deleted", "An environment has been successfully deleted")
		raise web.seeother( "environments.html" )

def env_types():
	return db().execute( "Environment_Forms", 8, [] )

def free_servers( eid = 0 ):
	return db().execute( "Environment_Forms", 9, [eid] )

def selected_servers( eid ):
	return [value for row in db().execute( "Environment_Forms", 10, [eid] ) for value in row]


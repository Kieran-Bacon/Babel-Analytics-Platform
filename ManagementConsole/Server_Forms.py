import web
import HelperFunctions as help
from os.path import isfile, join
from AnalyticsServerInterface import Server
from DatabaseHandler import DatabaseHandler as db
from os import mkdir, listdir, rename, remove, rmdir

render = web.template.render('templates')

class Add_Server:
	def GET(self):
		help.check_access()
		return help.renderPage( 'Add Server', render.add_server( "New", env_data(), [] ) )
	
	def POST(self):
		help.check_access()
		
		# Extract the information from the post message and test to see if valid.
		input = web.input(machine_name="NULL"
			, desc_text="NULL"
			, machine_address="NULL"
			, a_port_num="NULL"
			, m_port_num="NULL"
			, ssh_port_num="NULL"
			, eid=0
			, ssh_username="NULL"
			, ssh_password="NULL"
			, ssh_key_address="NULL"
			)

		serverInfo = [
			  input.eid
			, input.machine_name
			, input.desc_text
			, input.machine_address
			, input.a_port_num
			, input.m_port_num
			, input.ssh_port_num
			, input.ssh_username
			, input.ssh_password
			, input.ssh_key_address
			]

		if ("NULL" in serverInfo[:6]) or (serverInfo[7] == "NULL" and serverInfo[8] == "NULL"):
			help.append_user_alerts('error', 'Invalid Inputs', 'Please ensure that all the inputs are correct, and try again.')
			return help.renderPage( "Add Server", render.add_server( "New", env_data(), serverInfo ))

		# Open a connection with the server and check to see if it exits.
		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}
		server = Server( input.machine_address, int(input.m_port_num) )
		status = server.send( "GET", "/STATUS/*", msgHeaders )
		if status == "FAILED" or status[0] != "200":
			help.append_user_alerts('error', 'Connection Error', 'Either the server is not currently accepting requests or the information input is invalid, please check both and try again.')
			return help.renderPage( "Add Server", render.add_server( "New", env_data(), serverInfo ))

		# Add Server into the database and collect the master Config of the Server.
		ID = db().executeID( "Server_Forms", 2, serverInfo)
		resp = server.retrieveMaster( msgHeaders, ID, input.ssh_username, input.ssh_password )
		if( resp == -1 ):
			db().executeLiteral( "DELETE FROM servers WHERE srv_id = ?", [ID])
			help.append_user_alerts('error', 'Invalid Authentication Information', 'The ssh information entered was not valid, connection was rejected.')
			return help.renderPage( "Add Server", render.add_server( "New", env_data(), serverInfo ))

		server.getLogs( ID, msgHeaders, input.ssh_username, input.ssh_password )

		# Report success
		help.append_user_alerts('success','Successfully Added', 'Your new server "'+ input.machine_name+'" has been added into the system.')
		raise web.seeother("/manage_servers.html")

class Edit_Server:
	def GET( self, sid ):
		help.check_access()
		serverInfo = list((db().execute("Server_Forms", 3, [sid]))[0])
		return help.renderPage( 'Add Server', render.add_server( sid, env_data(), serverInfo[1:] ) )

	def POST( self, sid ):
		help.check_access()
		
		# Extract information from the post request and validate.
		input = web.input(machine_name="NULL"
			, desc_text="NULL"
			, machine_address="NULL"
			, a_port_num="NULL"
			, m_port_num="NULL"
			, ssh_port_num="NULL"
			, eid="0"
			, ssh_username="NULL"
			, ssh_key_address="NULL"
			)

		# The password on the page is editted to be incorrect.
		# Password to be changed by high level users in the future.
		ssh_password = db().executeLiteral("SELECT ssh_password FROM servers WHERE srv_id = ?", [sid] )[0][0]
		serverInfo = [ int(input.eid)
			, input.machine_name
			, input.desc_text
			, input.machine_address
			, int( input.a_port_num )
			, int( input.m_port_num )
			, int( input.ssh_port_num )
			, input.ssh_username
			, ssh_password
			, input.ssh_key_address
			]

		if any((x == "NULL") for x in serverInfo[0:6]) or (serverInfo[7] == "NULL" and serverInfo[8] == "NULL"):
			raise web.BadRequest();

		# Open a connection with the server and check to see if it exits.
		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}
		server = Server( input.machine_address, int(input.m_port_num) )
		status = server.send( "GET", "/STATUS/*", msgHeaders )
		if status == "FAILED" or status[0] != "200":
			help.append_user_alerts('error', 'Connection Error', 'Either the server is not currently accepting requests or the information input is invalid, please check both and try again.')
			return help.renderPage( "Add Server", render.add_server( sid, env_data(), serverInfo ))
		
		# Collect and replace the master Config of the Server.
		resp = server.retrieveMaster( msgHeaders, sid, input.ssh_username, ssh_password )
		if( resp == -1 ):
			help.append_user_alerts('error', 'Invalid Authentication Information', 'The ssh information entered was not valid, connection was rejected.')
			return help.renderPage( "Add Server", render.add_server( "New", env_data(), serverInfo ))

		server.getLogs( sid, msgHeaders, input.ssh_username, ssh_password )

		# Update Server with Services if change of environment.
		OriginalInfo = db().executeLiteral( "SELECT * FROM servers WHERE srv_id = ?", [sid] )[0]

		if( OriginalInfo[1] != int(input.eid) ):
			currentServices = db().executeLiteral( "SELECT sv.sid, ser.resource_name FROM services ser, services_versions sv, service_deployment_lkp sdl, servers srv WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = srv.eid AND srv.srv_id = ? GROUP BY ser.sgid ORDER BY sv.version DESC", [sid])
			newServices = db().executeLiteral( "SELECT sv.sid, ser.service_name, ser.resource_name, sv.version, sv.main_script, sv.language, sv.poolsize, sv.get_html_file, sv.get_redirect FROM services ser, services_versions sv, service_deployment_lkp sdl WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = ? GROUP BY ser.sgid ORDER BY sv.version DESC", [input.eid] )
			
			cIDs = [x[0] for x in currentServices ]
			nIDs = [x[0] for x in newServices ]

			print( cIDs )
			print( nIDs )

			deleteing = [ x for x in cIDs if x not in nIDs ]
			creating = [ x for x in nIDs if x not in cIDs ]

			for service in currentServices:
				if service[0] in deleteing:
					resp = server.send( "DELETE", service[1], msgHeaders )
					print( resp )

			for service in newServices:
				if service[0] in creating:
					if service[8] != "NULL":
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
					    "HTML":HTML 
					}
					directory = join( "./services", str( service[0] ), str( service[3] ) )
					resp = server.createService( msgHeaders, input.ssh_username, ssh_password, directory, data )

		# Update info
		db().executeLiteral( "UPDATE servers SET eid = ?, display_name = ?, description = ?, machine_address = ?, a_port_num = ?, m_port_num = ?, ssh_port_num = ?, ssh_username = ?, ssh_password = ?, ssh_key_address = ? WHERE srv_id = ? ", serverInfo + [sid] )

		help.append_user_alerts('success','Successfully Edited', 'You have changes information for "'+ input.machine_name+'"')
		raise web.seeother("/manage_servers.html")

class Delete_Server:
	def GET( self, srv_id ):

		# Tell server to delete its contents
		address, port = db().executeLiteral( "SELECT machine_address, m_port_num FROM servers WHERE srv_id = ?", [srv_id] )[0]
		resources = [ x[0] for x in db().executeLiteral( "SELECT ser.resource_name FROM services ser, services_versions sv, service_deployment_lkp sdl, servers srv WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = srv.eid AND srv.srv_id = ? GROUP BY ser.sgid", [srv_id])]

		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}
		
		interface = Server( address, port )
		for res in resources:
			interface.send( "DELETE", res, msgHeaders )

		# Delete Config
		try:
			remove( join( "./configs", srv_id ) )
		except:
			web.debug("Tried to delete Analytics config but it was not found!")

		# Delete log files
		logLoc = join( "./logs", srv_id )
		try:
			logs = listdir( logLoc )
			for log in logs:
				remove( join( logLoc, log ) )
			rmdir( logLoc )
		except:
			web.debug( "Tried to delete log files at " + logLoc + " but they didn't exist." )

		# Delete from database
		db().execute( "Server_Forms", 4, [srv_id])

		help.append_user_alerts('default','Successfully Deleted', "Some server information has been deleted? (get it! :P we don't even know what server it was!)")
		raise web.seeother("/manage_servers.html")

def env_data():
	types = db().execute( "Server_Forms", 0, [])
	data = []
	inner_data = []
	for env_type in types:
		inner_data = [env_type['name']]

		envs = list(db().execute( "Server_Forms", 1, [env_type['name']]))
		
		for env in envs:
			inner_data.append( env )
		data.append( inner_data )

	return data
import web
import sqlite3
import HelperFunctions as help
from AnalyticsServerInterface import Server, findPaths
from DatabaseHandler import DatabaseHandler as db
from System_Information import System_Information as si 
from os import stat, mkdir, listdir, rename, remove, rmdir
from os.path import isfile, join

render = web.template.render('templates')

class Add_Service:
	def GET(self):
		#Return service add form
		help.check_access()
		redirect()
		paths = db().executeLiteral( "SELECT pid, name FROM paths", [])
		return help.renderPage( "Add Service", render.service_version_form( [] , [], paths, si().getVersion() ) )

	def POST(self):
		#Service add form submit
		help.check_access()
		redirect()

		input = web.input( service_name="NULL",
						   resource_name="NULL",
						   description="NULL",
						   poolsize="NULL",
						   language="NULL",
						   main_script="NULL",
						   get_page_select="NULL",
						   redirect_URL="NULL",
						   pid="NULL" )

		# Define location of temp files uploaded.
		tempLocation = join( "./temp/uploads/", (web.ctx.session).username )

		if not validateService( input.service_name, input.resource_name) :
			# name or resource taken, delete files and move on.
			clearDir( tempLocation )
			raise web.seeother( "add_service.html" )

		# Create the service information and run it against the database
		service_info = [
			int(input.pid),
			input.service_name,
			input.resource_name,
			input.description
		]
		sgid = db().executeID( "Service_Forms", 0, service_info)

		# Create the service version information.
		if (input.get_page_select == "NULL" or input.get_page_select == "") and input.redirect_URL == "NULL":
			# The event when neither a dashboard or a redirect is given.
			sredirect = "www.google.com"
		else:
			sredirect = input.redirect_URL
		version_info = [
			sgid,
			si().getVersion(),
			int( input.poolsize ),
			help.convert_lang( input.language ),
			input.main_script,
			input.get_page_select,
			sredirect
		]

		if ("NULL" in service_info or "NULL" in version_info[:5]):
			db().executeLiteral( "DELETE FROM services WHERE sgid = ?", [sgid])
			clearDir( tempLocation )
			help.append_user_alerts( "warning", "Invalid information", "The information passes is invalid, please retry.")
			return web.seeother("add_service.html")

		# Move files to the correct location.
		moveFiles( sgid, si().getVersion(), input.uploaded_files )
		serviceLocation = join( "./services", str(sgid), str(si().getVersion()) )

		# Promote to the first environment.
		eid = db().executeLiteral( "SELECT eid FROM env_path_lkp WHERE pid = ? ORDER BY position ASC", [input.pid] )[0][0]
		envServers = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password, display_name FROM servers WHERE eid = ?", [eid])

		# Construct service data.
		if input.redirect_URL != "NULL":
			status = 303
			html = sredirect
		else:
			status = 200
			html = input.get_page_select
		data = { 
			"name": input.service_name,
			"resource": input.resource_name,
			"status": "ACTIVE",
			"version": help.strVersion( si().getVersion() ),
			"mainScript": input.main_script,
			"language": help.convert_lang( input.language ),
			"poolSize": input.poolsize, 
			"HTTP_Status": status, 
			"HTML": html 
		}

		# Push to every server but check to ensure that the servers accept it.

		msgHeaders = {"Username": web.ctx.session.username, "Access-Token": web.ctx.session.access_token }

		count = len( envServers )

		print( count )
		for server in envServers:
			resp = Server( server[0], server[1] ).createService( msgHeaders, server[2], server[3], serviceLocation, data )

			# The Service was not deployed successfully.
			if resp == -1:
				help.append_user_alerts( "warning", "Connection Error!", "Could not form a connection with " + server[4] + "." )
				count -= 1
			elif resp[0] != "200":
				help.append_user_alerts( "warning", "Server rejected!", "The Server " + server[4] + " has reported that the service was not successfully installed! Reason being: "+ resp[1] )
				count -= 1

		sid = db().executeID( "Service_Forms", 1, version_info )
		if count > 0:
			# Add the service version into the database and append it to deployed.
			db().executeLiteral( "INSERT INTO service_deployment_lkp VALUES ( ?,?,? )", [eid, sid, "ACTIVE"] )
		else:
			# No server accepted it so officially
			help.append_user_alerts( "info", "Created but not Deployed","The service was created but was not successfully deployed to the first environment.") 
			return "add_service.html"

		# Return a success
		help.append_user_alerts('info', 'Operation Successful', 'You have sucessfully created the new service: ' + input.service_name +'.')
		return "service_details_" + str( sgid )

class Edit_Service:
	# Editting Service group information.

	def GET( self, sgid ):
		help.check_access()
		redirect()
		paths = db().executeLiteral( "SELECT pid, name FROM paths", [])
		data = db().executeLiteral( "SELECT * FROM services WHERE sgid = ?", [sgid] )[0]
		return help.renderPage( "Edit Service", render.service_group_form( sgid, data, paths ))

	def POST( self, sgid):
		help.check_access()
		redirect()

		# Get current path information incase of path change.
		pid, name, resource = db().executeLiteral( "SELECT pid, service_name, resource_name FROM services WHERE sgid = ?", [sgid] )[0]

		# Extract information and validate
		input = web.input( pid="NULL", service_name="NULL", description="NULL" )
		service_info = [
			input.pid,
			input.service_name,
			resource,
			input.description,
			int(sgid)
		]
		if "NULL" in service_info:
			help.append_user_alerts( "warning", "Invalid Input", "The information given is invalid, please try again." )
			paths = db().executeLiteral( "SELECT pid, name FROM paths", [])
			return help.renderpage( "Edit Service", render.edit_service( sgid , [int(sgid)] + service_info , paths ))

		if int(input.pid) != int(pid):

			# In prep for server communication
			usr = (web.ctx.session).username
			token = (web.ctx.session).access_token
			msgHeaders = { "Username": usr, "Access-Token":token} 

			# Service has changed path and therefore needs to have the service versions changed.
			oldPathEnv = [ int(x[0]) for x in db().executeLiteral("SELECT eid FROM env_path_lkp WHERE pid = ?", [pid] )]
			newPathEnv = [ int(x[0]) for x in db().executeLiteral("SELECT eid FROM env_path_lkp WHERE pid = ?", [input.pid] )]
			Removed = [ x for x in oldPathEnv if x not in newPathEnv ]
			Persist = [ x for x in newPathEnv if x in oldPathEnv ]
			Added = [ x for x in newPathEnv if x not in oldPathEnv ]

			# Remove from the top of the path the environments that will not need to be added too.
			# Reverse it so that the top environment is at the front ( just cus )
			Cropped = newPathEnv[: newPathEnv.index( Persist[-1] )+1 ][::-1]

			print( Removed, Persist, Added, Cropped )

			# Remove from old environments and decouple
			for eid in Removed:
				# Remove the service from all servers on the environment.
				envServers = db().executeLiteral( "SELECT machine_address, m_port_num FROM servers WHERE eid = ?", [eid])
				for server in envServers:
					Server( server[0], server[1] ).send( "DELETE", resource, msgHeaders );

				# Delete all services on that environment that are of this service.
				db().executeLiteral( "DELETE FROM service_deployment_lkp WHERE eid = ? AND sid IN ( SELECT sid FROM services_versions WHERE sgid = ? )", [eid, sgid] )

			# Add Services to new servers if needed too, replace if needed too and so on.
			topVer = [ 0,0,0,0,0,0,0 ]
			for eid in Cropped:
				# Get Servers on environment.
				servers = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password FROM servers WHERE eid = ?", [eid] )
				# Get the current version running on machine.
				current = db().executeLiteral( "SELECT sv.sid, sv.version, sv.main_script, sv.language, sv.poolsize, sv.get_html_file, sv.get_redirect FROM services_versions sv, service_deployment_lkp sdl WHERE sv.sgid = ? AND sv.sid = sdl.sid AND sdl.eid = ? ORDER BY sv.version DESC", [sgid, eid] )

				print( len( current ) )
				for i in current:
					print i[1]

				if len( current ) != 0 :
					if topVer[1] <= current[0][2]:
						# Current version is better therefore leave it.
						topVer = current[0]
						continue
					else:
						# Version is worse, Delete Version.
						for server in servers:
							Server( server[0], server[1] ).send( "DELETE", resource, msgHeaders)

				# No version on machine therefore push topVersion
				
				if topVer[6] != "NULL":
					status = 303
					html = topVer[6]
				else:
					status = 200
					html = topVer[5]
				data = { "name": name,
						 "resource": resource,
						 "status": "ACTIVE",
						 "version": topVer[1],
						 "mainScript": topVer[2],
						 "language": topVer[3],
						 "poolSize": topVer[4],
						 "HTTP_Status": status, 
						 "HTML": html }

				for server in servers:
					service_location = join( "./services", str(sgid), str(topVer[1]) )
					resp = Server( server[0], server[1]).createService( msgHeaders, server[2], server[3], service_location, data )
					print( resp )

				# Add to Database new push
				db().executeLiteral( "INSERT INTO service_deployment_lkp VALUES (?,?,?)", [eid, topVer[0], "ACTIVE" ])

		# Update the database 
		db().executeLiteral( "UPDATE services SET pid = ?, service_name = ?, resource_name = ?, description = ? WHERE sgid = ?", service_info )

		# Inform the user and return
		help.append_user_alerts('info', 'Operation Successful', 'You have sucessfully edited the service: ' + input.service_name +'.')
		return web.seeother( "manage_services.html" )

class Delete_Service:
	def GET(self, sgid):
		help.check_access()

		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}

		# Collect the resouce of the service.
		resource = db().executeLiteral( "SELECT resource_name FROM services WHERE sgid = ?", [sgid] )[0][0]
		# Collect a list of all servers the service is running on.
		servers = db().executeLiteral( "SELECT srv.machine_address, srv.m_port_num FROM services_versions sv, service_deployment_lkp sdl, servers srv WHERE sv.sgid = ? AND sv.sid = sdl.sid AND sdl.eid = srv.eid GROUP BY srv.srv_id", [sgid] )
		# Delete the resource on every server
		for eachServer in servers:
			Server( eachServer[0], eachServer[1] ).send( "DELETE", resource, msgHeaders )

		# Delete local for service.
		clearDir( join( "./services", str(sgid) ) )

		# Decouple Database
		db().executeLiteral( "DELETE FROM services WHERE sgid = ?", [sgid])
		db().executeLiteral( "DELETE FROM service_deployment_lkp WHERE sid IN (SELECT sid FROM services_versions WHERE sgid = ?)", [sgid] )
		db().executeLiteral( "DELETE FROM services_versions WHERE sgid = ?", [sgid] )

		help.append_user_alerts( "info", "Successfully Deleted", "We have successfully deleted the service information." )
		raise web.seeother( "manage_services.html" )

class Add_Version:
	def GET( self, sgid ):
		help.check_access()
		redirect()

		# Geting paths
		paths = db().executeLiteral( "SELECT pid, name FROM paths", [] )
		# Adding new version to set sgid. Get Current highest version
		version = db().executeLiteral( "SELECT version FROM services_versions WHERE sgid = ? ORDER BY version DESC", [sgid] )
		if len( version ) > 0:
			version = version[0][0]
		else:
			version = si().getVersion()

		# Get the service group info.
		groupInfo = db().executeLiteral( "SELECT * FROM services WHERE sgid = ?", [sgid] )[0]
		return help.renderPage( "Add Version", render.service_version_form( [0, sgid], groupInfo, paths, version ))

	def POST( self, sgid ):
		help.check_access()
		redirect()

		# For adding a new version we only care about version information.
		input = web.input( version="NULL", poolsize="NULL",
						   language="NULL", main_script="NULL", uploaded_files="NULL",
						   get_page_select="NULL", redirect_URL="NULL" )

		name, resource, eid = db().executeLiteral( "SELECT ser.service_name, ser.resource_name, epl.eid FROM services ser, paths p, env_path_lkp epl WHERE ser.sgid = ? AND ser.pid = p.pid AND p.pid = epl.pid ORDER BY epl.position ASC", [sgid] )[0]
		topVersion = db().executeLiteral( "SELECT sv.version FROM services_versions sv WHERE sv.sgid = ? ORDER BY sv.version DESC", [sgid] )

		if len( topVersion ) == 0:
			versionNum = int( input.version )
		else:
			if int( input.version ) <= int( topVersion[0][0] ):
				versionNum = topVersion[0][0] + 1
			else:
				versionNum = int( input.version )

		version_info = [
			int(sgid),
			versionNum,
			int(input.poolsize),
			help.convert_lang( input.language ),
			input.main_script,
			input.get_page_select,
			input.redirect_URL
		]

		if "NULL" in version_info[:4]:
			help.append_user_alerts( "warning", "Invalid Inputs", "Some of the inputs are invalid, check them and try again." )
			paths = db().executeLiteral( "SELECT pid, name FROM paths" )
			return help.renderPage( "Add Version", render.service_version_form( [0, sgid], [0] + version_info, paths, version ))


		# Move files from temp to the newly created version space.
		moveFiles( sgid, versionNum, input.uploaded_files )
		location = join( "./services", str( sgid ), str( versionNum ) )

		# Delete previous version if any on starting server and push new version.
		servers = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password, display_name FROM servers WHERE eid = ?", [eid] )
		versionCheck = db().executeLiteral( "SELECT count(*) FROM services_versions sv, service_deployment_lkp sdl WHERE sv.sgid = ? AND sv.sid = sdl.sid AND sdl.eid = ?", [sgid, eid] )[0][0]

		msgHeaders = { "Username": (web.ctx.session).username, "Access-Token":(web.ctx.session).access_token}

		count = len( servers )
		for server in servers:
			interface = Server( server[0], server[1] )

			if versionCheck > 0:
				interface.send( "DELETE", resource, msgHeaders )

			if input.redirect_URL != "NULL":
				status = 303
				html = input.redirect_URL
			else:
				status = 200
				html = input.get_page_select
			data = { 
				"name": name,
				"resource": resource,
				"status": "ACTIVE",
				"version": versionNum,
				"mainScript": input.main_script,
				"language": help.convert_lang( input.language ),
				"poolSize": input.poolsize,
				"HTTP_Status": status, 
				"HTML": html 
			}

			resp = interface.createService( msgHeaders, server[2], server[3], location, data )

			if resp == -1:
				help.append_user_alerts( "warning", "Unable to make Connection!", "A connection to the server " + server[4] + " could not be made! Service not installed." )
				count -= 1
			elif resp[0] != "200":
				help.append_user_alerts( "warning", "Server rejected new version", server[4] + " has rejected the installation of the service. Reason being: " + resp[1] )
				count -= 1

		sid = db().executeID( "Service_Forms", 1, version_info )

		if count > 0:
			db().executeLiteral( "INSERT INTO service_deployment_lkp VALUES ( ?,?,? )", [eid, sid, "ACTIVE"] )
			return "service_details_" + str( sgid )
		else:
			help.append_user_alerts( "warning", "Service not deployed", "No server accepted the service, it is currently not deployed." )
			return "service_details_" + str( sgid )

""" 
############################################
##           Deprecated Class             ##
############################################
class Edit_Version:
	def GET( self, sid ):
		help.check_access()
		redirect()

		validCheck = db().executeLiteral( "SELECT count(*) FROM service_deployment_lkp sdl, environments env WHERE sdl.sid = ? AND sld.eid = env.eid AND env.env_type <> 'DEV'", [sid] )[0][0]

		if validCheck > 0:
			help.append_user_alerts( "warning", "Too far in Path", "The version is currently on non development environments and therefore it would potentially damagine to edit in place, either demote and try again or create a new version")
			raise web.seeother( "manage_services.html" )

		version = db().executeLiteral( "SELECT version FROM services_versions WHERE sid = ?", [sid] )
		groupInfo = db().executeLiteral( "SELECT ser.* FROM services ser, services_versions sv WHERE ser.sgid = sv.sgid AND sv.sid = ?", [sid] )
		return help.renderPage( "Edit Version", render.service_version_form( [1,sid], groupInfo, getPaths(), version ))

	def POST(self, sid):
		help.check_access()
		redirect()

		 validCheck = db().executeLiteral( "SELECT count(*) FROM service_deployment_lkp sdl, environments env WHERE sdl.sid = ? AND sld.eid = env.eid AND env.env_type <> 'DEV'", [sid] )[0][0]

		if validCheck > 0:
			help.append_user_alerts( "warning", "Too far in Path", "The version is currently on non development environments and therefore it would potentially damagine to edit in place, either demote and try again or create a new version")
			raise web.seeother( "manage_services.html" )

		input = web.input( version="NULL", poolsize="NULL",
						   language="NULL", main_script="NULL", uploaded_files="NULL",
						   get_page_select="NULL", redirect_URL="NULL" )

		originalService = db().executeLiteral( "SELECT * FROM services_versions WHERE sid = ?", [sid] )

		version_info = [
			version,
			int(input.poolsize),
			help.convert_lang( input.language ),
			input.main_script,
			input.get_page_select,
			input.redirect_URL,
			sid
		]


		db().execute( "Service_Forms",6, version_info)
		clearDir( file_location )
		moveFiles( sgid, version, input.uploaded_files )

		return 200
"""


class Delete_Version:
	def GET(self, sid):
		help.check_access()

		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}

		# Collect the service resouce
		service = db().executeLiteral( "SELECT ser.sgid, ser.resource_name, sv.version FROM services ser, services_versions sv WHERE ser.sgid = sv.sgid AND sv.sid = ?", [sid])[0]
		# Collect Environment ids where the service may be running.
		environments = [ x[0] for x in db().executeLiteral( "SELECT eid FROM service_deployment_lkp WHERE sid = ?", [sid])]

		for env in environments:
			# Pull out the servers on the environment.
			servers = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password FROM servers WHERE eid = ?", [ env ])
			# Pull out the version running on the environment
			competition = db().executeLiteral( "SELECT ser.sgid, ser.service_name, ser.resource_name, sv.version, sv.main_script, sv.language, sv.poolsize, sv.get_html_file, sv.get_redirect FROM services ser, services_versions sv, service_deployment_lkp sdl WHERE ser.sgid = ? AND ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = ? ORDER BY sv.version DESC", [ service[0], env ])
			
			if len(competition) == 1:
				# Service is only one running.

				for server in servers:
					# Delete the resource on every server.
					Server( server[0], server[1] ).send( "DELETE", service[1], msgHeaders )

			else:
				# Extract the running service and the back up.
				top = competition[0]
				backup = competition[1]

				print( service[2], top[3] )

				if service[2] == top[3]:
					# Service is the running service

					for server in servers:
						interface = Server( server[0], server[1] )
						# Delete the resource on every server.
						interface.send( "DELETE", service[1], msgHeaders )


						print( backup[7], backup[8] )
						# Push backup
						if backup[7] == 'NULL' or (backup[8] != "NULL" and backup[8] != ''):
							status = 303
							HTML = backup[8]
						else:
							status = 200
							HTML = backup[7]
						data =  {
							"name": backup[1],
							"resource": backup[2],
							"status": "ACTIVE",
							"version": backup[3], 
							"mainScript":backup[4], 
							"language":backup[5], 
						    "poolSize":backup[6], 
						    "HTTP_Status":status, 
						    "HTML" : HTML
						}

						location = join( "./services", str( backup[0] ), str( backup[3] ) )
						interface.createService( msgHeaders, server[2], server[3], location, data )

		# Delete Files
		clearDir( join( "./services", str(service[0]), str(service[2]) ) )

		# Decouple Database
		db().executeLiteral( "DELETE FROM services_versions WHERE sid = ?", [sid])
		db().executeLiteral( "DELETE FROM service_deployment_lkp WHERE sid = ?", [sid])

		raise web.seeother( "/service_details_" + str( service[0] ))

def validateService( name, resource ):
	nCount = db().executeLiteral( "SELECT count(*) FROM services WHERE service_name = ?", [name])[0][0]
	rCount = db().executeLiteral( "SELECT count(*) FROM services WHERE resource_name = ?", [name])[0][0]
	if (nCount + rCount) != 0:
		help.append_user_alerts( "warning","Invalid Input", "The service name or resource have already been taken, please either select alternatives or free the service before proceeding.")
		return False
	return True

def moveFiles( sgid, version, file_list):
		usr = (web.ctx.session).username
		service_location = join("./services", str(sgid) )
		temp_location = join( "./temp/uploads", usr )

		try:
			stat( service_location )
		except:
			mkdir( service_location )

		service_location = join( service_location, str(version) )

		try:
			stat( service_location )
		except:
			mkdir( service_location )

		for file in file_list.split(','):
			try:
				rename( join( temp_location, file), join( service_location, file) )
			except:
				web.debug( "Error on file: " + file )

def clearDir( dir ):
	dirs, paths = findPaths( dir )
	for file in paths:
		remove( file )
	for folder in dirs[::-1]:
		rmdir ( folder )
	rmdir( dir )  

def redirect():
	count = db().executeLiteral( "SELECT count(*) FROM paths", [])[0][0]
	if(count == 0):
		help.append_user_alerts('info', 'Need a Development path first!', 'You cannot create a new service without having a path to follow, please create one now.')
		raise web.seeother( "path_form_0" )
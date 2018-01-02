import web
from os.path import join
import HelperFunctions as help
from AnalyticsServerInterface import Server
from DatabaseHandler import DatabaseHandler as db


render = web.template.render('templates')

class Path_Details:
	
	def GET( self, pid ):
		help.check_access()

		dev = [name for row in db().execute( "Path_Details", 0, ['DEV', pid]) for name in row]
		test = [name for row in db().execute( "Path_Details", 0, ['TEST', pid]) for name in row]
		stage = [name for row in db().execute( "Path_Details", 0, ['STAGING', pid]) for name in row]
		live = [name for row in db().execute( "Path_Details", 0, ['LIVE', pid]) for name in row]

		selected = [ dev, test, stage, live]

		ns_dev = [name for row in db().execute( "Path_Details", 1, ['DEV']) for name in row if not name in dev ]
		ns_test = [name for row in db().execute( "Path_Details", 1, ['TEST']) for name in row if not name in test]
		ns_stage = [name for row in db().execute( "Path_Details", 1, ['STAGING']) for name in row if not name in stage]
		ns_live = [name for row in db().execute( "Path_Details", 1, ['LIVE']) for name in row if not name in live]

		not_selected = [ ns_dev, ns_test, ns_stage, ns_live ]

		path_info = db().execute( "Path_Details", 2, [pid])[0]

		return help.renderPage( "Path Details", render.path_details( path_info, not_selected, selected ))

class AJAX_Path_Update:

	def POST( self, pid ):
		help.check_access()

		input = web.input( dev='', test='', stage='', live='' )

		# Define permissions for server interactions.
		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}

		# Determine removed environments and newly added environments.
		originalEnvs =[ x[0] for x in db().executeLiteral("SELECT eid FROM env_path_lkp WHERE pid = ? ORDER BY position DESC", [pid] )][::-1]

		newEnvs = []
		sections = [ input.dev, input.test, input.stage, input.live ]
		for sec in sections:
			array = sec.split(',')
			for name in array:
				if( name == '' ): break
				output = db().executeLiteral( "SELECT eid FROM environments WHERE name = ?", [name])[0]
				if( len( output ) != 0):
					newEnvs.append( output[0] )

		removed = [ x for x in originalEnvs if x not in newEnvs ]
		persist = [ x for x in newEnvs if x in originalEnvs ]
		added = [ x for x in newEnvs if x not in originalEnvs ]

		if len( added ) != 0 and len( persist ) > 0:
			# There are some added environments, and some evironments remain from the original.
			cropped = newEnvs[: newEnvs.index( persist[-1] ) + 1 ][::-1]
		else:
			cropped = []

		# Delete resouce from all removed environments.
		for env in removed:
				# Get Every Server in the environment info.
				envServers = db().executeLiteral( "SELECT machine_address, m_port_num FROM servers WHERE eid = ?", [env] )
				# Get Every Service on the path on that environment
				envServices = db().executeLiteral( "SELECT sv.sid, ser.resource_name FROM services ser, services_versions sv, service_deployment_lkp sdl WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = ? AND ser.pid = ? GROUP BY ser.sgid ORDER BY sv.version DESC", [env, pid] )

				for eachServer in envServers:
					server = Server( eachServer[0], eachServer[1] )

					for eachService in envServices:
						server.send( "DELETE", eachService[1], msgHeaders )

						# Decouple service and environment. 
						db().executeLiteral( "DELETE FROM service_deployment_lkp WHERE sid = ? AND eid = ?", [eachService[0], env] )

		# Get the sgid for every service on the path and create holder.
		best = [[x[0],0,0,0,0,0,0,0,0,0] for x in db().executeLiteral( "SELECT sgid FROM services WHERE pid = ?", [pid])]
		for env in cropped:
			# Get a list of all servers for this environment.
			envServers = db().executeLiteral( "SELECT machine_address, m_port_num, ssh_username, ssh_password FROM servers WHERE eid = ?", [env])

			# For each of the services do the good stuff.
			for i in range( len(best) ):
				# Extract the service information.
				serviceG = best[i]
				# Get the best version of that service group that is running on that machine.
				running = db().executeLiteral( "SELECT sv.sid, ser.service_name, ser.resource_name, sv.version, sv.main_script, sv.language, sv.poolsize, sv.get_html_file, sv.get_redirect FROM services ser, services_versions sv, service_deployment_lkp sdl WHERE ser.sgid = sv.sgid AND sv.sid = sdl.sid AND sdl.eid = ? AND ser.sgid = ? GROUP BY ser.sgid ORDER BY sv.version DESC", [env, serviceG[0]])
				
				print( env, len( running ))

				count = 1
				if len( running ) == 0 or running[0][4] < serviceG[4]:
					# Service needs to be pushed too.
					if len( running ) != 0:
						# Service running was old.
						for ser in envServers:
							Server( ser[0], ser[1] ).send( "DELETE", serviceG[3], msgHeaders )

					print( "length " , len( serviceG ))
					print( serviceG )

					if serviceG[1] == 0:
						# Service not set yet
						print( "NOT SET NOT SET" )
						continue

					# Construct Data for push
					if serviceG[8] == "NULL":
						status = 303
						HTML = serviceG[9]
					else:
						status = 200
						HTML = serviceG[8]
					data =  {
						"name": serviceG[2],
						"resource": serviceG[3],
						"status": "ACTIVE",
						"version": serviceG[4],
						"mainScript":serviceG[5],
						"language":serviceG[6],
						"poolSize":serviceG[7],
						"HTTP_Status":status,
						"HTML":HTML
					}

					print( data )

					location = join( "./services", str( serviceG[0] ), str( serviceG[4]) )
					count = len( envServers )
					for ser in envServers:
						resp = Server( ser[0], ser[1] ).createService( msgHeaders, ser[2], ser[3], location, data )
						
						if resp == -1 or resp[0] != "200":
							web.debug( resp )
							count -= 1
				else:
					# It was a better serivce, replace it.
					best[i] = [ best[i][0] ] + list( running[0] )
					serviceG = best[i]

				# Pushed or not the services is now coupled with environment if linked correctly.
				if count > 0:
					if env not in persist:
						db().executeLiteral( "INSERT INTO service_deployment_lkp VALUES ( ?,?,?) ", [env, serviceG[1], "ACTIVE"])
				else:
					help.append_user_alerts( "warning", "Service not deployed", serviceG[2] + " was not deployed onto an environment." )
				
		# Delete all path environments and correctly increment the new path.
		db().executeLiteral( "DELETE FROM env_path_lkp WHERE pid = ?", [pid] )
		pos = 1
		for env in newEnvs:
			db().executeLiteral( "INSERT INTO env_path_lkp VALUES ( ?,?,? )", [pid, env, pos])
			pos += 1
		db().executeLiteral( "UPDATE paths SET length = ? WHERE pid = ?", [ len(newEnvs), pid ])

		help.append_user_alerts( 'info', 'Updated sucessfully', 'The path information has been updated.')
		return 200
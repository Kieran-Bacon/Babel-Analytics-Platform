import web
from DatabaseHandler import DatabaseHandler as db
from AnalyticsServerInterface import Server

import HelperFunctions as help

class Activate_Service:
	def POST(self):
		help.check_access()

		# Collect and verity input information.
		input = web.input( eid="NULL", sid="NULL" )
		if input.eid == "NULL" or input.sid == "NULL":
			raise web.badrequest()

		# Construct the message information plus target information.
		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}
		resource = "/ACTIVATE" + db().executeLiteral("SELECT ser.resource_name FROM services ser, services_versions srv WHERE srv.sid = ? AND srv.sgid = ser.sgid", [input.sid] )[0][0]
		Env_Ser = db().executeLiteral("SELECT display_name, machine_address, m_port_num FROM servers WHERE eid = ?", input.eid )


		# Activate the service on all targets.
		count = len(Env_Ser)
		for server in Env_Ser:
			resp = Server( server[1], server[2] ).send( "GET", resource, msgHeaders )
			print "RESPONSE FROM SERVER"
			print resp 
			if resp == "FAILED" or resp[0] != "200":
				help.append_user_alerts("warning", "Whoops", "Error on communicating with " + server[0] )
				count -= 1

		if count == 0:
			#None of the services were correctly activated, do not change stored status.
			help.append_user_alerts( "danger", "Unable to activate", "The service has not been correctly activated on any server of the environment.")
		else:
			# Update the database of the change
			db().executeLiteral("UPDATE service_deployment_lkp SET status = 'ACTIVE' WHERE eid = ? AND sid = ?", [input.eid, input.sid] )
		raise web.seeother("/environment_details_"+input.eid)




class Deactivate_Service:
	def POST(self):
		help.check_access()

		# Collect input information
		input = web.input( eid="NULL", sid="NULL" )
		if input.eid == "NULL" or input.sid == "NULL":
			raise web.badrequest()

		# Construct the message information plus target information.
		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeaders = { "Username": usr, "Access-Token":token}
		resource = "/DEACTIVATE" + db().executeLiteral("SELECT ser.resource_name FROM services ser, services_versions srv WHERE srv.sid = ? AND srv.sgid = ser.sgid", [input.sid] )[0][0]
		Env_Ser = db().executeLiteral("SELECT display_name, machine_address, m_port_num FROM servers WHERE eid = ?", input.eid )

		# Activate the service on all targets.
		count = len(Env_Ser)
		for server in Env_Ser:
			resp = Server( server[1], server[2] ).send( "GET", resource, msgHeaders )
			print "RESPONSE FROM SERVER"
			print resp 
			if resp == "FAILED" or resp[0] != "200":
				help.append_user_alerts("warning", "Whoops", "Error on communicating with " + server[0] )
				count -= 1

		if count == 0:
			#None of the services were correctly activated, do not change stored status.
			help.append_user_alerts( "danger", "Unable to deactivate", "The service has not been correctly deactivated on any server of the environment.")
		else:
			# Update the database of the change
			db().executeLiteral("UPDATE service_deployment_lkp SET status = 'INACTIVE' WHERE eid = ? AND sid = ?", [input.eid, input.sid] )
		raise web.seeother("/environment_details_"+input.eid)
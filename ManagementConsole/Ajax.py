import web
import sqlite3
import HelperFunctions as help

from random import randint
import datetime


render = web.template.render('templates')

#######################################
###			  Service Details		###
#######################################

class AJAX_service_details:
	def GET( self, sgid):
		conn = sqlite3.connect('./data/site.db')
		c = conn.cursor()
		c.execute("SELECT DISTINCT env.eid, serv.version FROM services serv, env_path_lkp env, service_deployment_lkp deploy WHERE serv.sgid = ? AND serv.sid = deploy.sid AND deploy.eid = env.eid ORDER BY serv.version DESC",(sgid,))
		data = c.fetchall()

		versions = []
		requests_info = []
		for env_ver in data:

			#Get data from somewhere

			if env_ver[1] not in versions:
				versions.append( env_ver[1] )
				#append data...
				
				requests_info.append( [1,2,3,4,5,6,7] )
			else:
				index = versions.index( env_ver[1] )
				#add data to the all ready existing data.

		versions.reverse()
		json_message =  '{ "versions" : ' + str( versions ) + ', '
		json_message += ' "xAxis" : ' + '["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], '
		json_message += ' "data": ' + str( requests_info ) + ' }'

		return json_message

#######################################
###			  Deploy service		###
#######################################

class AJAX_deploy_service:
	def POST(self):

		input = web.input( sid="NULL", eid="NULL" )
		if input.sid == "NULL" or input.eid == "NULL":
			raise web.badRequest()

		conn = sqlite3.connect('./data/site.db')
		c = conn.cursor()

		c.execute("SELECT * FROM service_deployment_lkp WHERE eid = ? AND sid = ?",(input.eid,input.sid,))
		if c.rowcount > 0:
			raise web.badrequest()

		c.execute("SELECT * FROM services WHERE sid = ?",(input.sid,))
		service_info = c.fetchone()
		
		c.execute("SELECT * FROM servers WHERE eid = ?",(input.eid,))
		servers = c.fetchall()
		for server in servers:
			analytics_server = AnalyticsServer( server )
			response = analytics_server.new( doc_root, service_info )

		c.execute("INSERT INTO service_deployment_lkp VALUES (?,?)", (input.eid,input.sid,))
		#conn.commit()
		#conn.close()

		return '{"type":"success","title":"Successfully deployed","content":"The service has successfully been deployed to the target environment."}'

#######################################
###			  Activate Service		###
#######################################

class AJAX_activate_service:
	def POST(self):
		input = web.input()
		conn = sqlite3.connect('./data/site.db')
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		c.execute("SELECT * FROM service_deployment_lkp WHERE sid = ? AND eid = ?",(input.sid,input.eid,))
		if c.fetchone() != None:
			c.execute("SELECT * FROM services WHERE sid = ?",(input.sid,))
			service_info = c.fetchone()
			c.execute("SELECT * FROM servers WHERE eid = ?",(input.eid,))
			servers = c.fetchall()

			for server in servers:
				try:
					analytics_server = AnalyticsServer( server )
					response = analytics_server.activate( service_info['resource_name'] )
				except:
					return '{"type":"error","title":"Error during communication","content":"While sending the activate message an error occured"}'
				#TODO if any response is not success check server to see if service
				#present and still active, try to deactivate it again.
				#flag issue and return.

			return '{"type":"success","title":"Service Successfully activated","content":"The service was successfully deactivated on the environment"}'

		else:
			return '{"type":"error","title":"Error during environment check","content":"The service does not seem to be a member of that environment"}'

#######################################
###			  Deactivate Service	###
#######################################

class AJAX_deactivate_service:
	def POST(self):
		input = web.input()
		conn = sqlite3.connect('./data/site.db')
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		c.execute("SELECT * FROM service_deployment_lkp WHERE sid = ? AND eid = ?",(input.sid,input.eid,))
		if c.fetchone() != None:
			c.execute("SELECT * FROM services WHERE sid = ?",(input.sid,))
			service_info = c.fetchone()
			c.execute("SELECT * FROM servers WHERE eid = ?",(input.eid,))
			servers = c.fetchall()

			for server in servers:
				try:
					analytics_server = AnalyticsServer( server )
					response = analytics_server.deactivate( service_info['resource_name'] )
				except:
					return '{"type":"error","title":"Error during communication","content":"While sending the deactivate message an error occured"}'
				#TODO if any response is not success check server to see if service
				#present and still active, try to deactivate it again.
				#flag issue and return.

			return '{"type":"success","title":"Service Successfully Deactivated","content":"The service was successfully deactivated on the environment"}'

		else:
			return '{"type":"error","title":"Error during environment check","content":"The service does not seem to be a member of that environment"}'
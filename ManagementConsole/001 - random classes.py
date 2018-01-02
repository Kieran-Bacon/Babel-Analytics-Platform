import web
import sqlite3
import HelperFunctions as help

render = web.template.render('templates')

class check_servicename:
	def POST(self):
		sn = web.input(servicename=None).servicename
		if sn is not None:
			conn = sqlite3.connect('./data/site.db')
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			c.execute("SELECT * FROM services WHERE service_name = ?",(sn,))
			if c.rowcount <= 0:
				conn.close()
				return True

		return False

class deactivate_service:
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
				analytics_server = AnalyticsServer( server )
				response = analytics_server.deactivate( service_info['resource_name'] )

			append_user_alerts("info",'Server Message',"Server response " + response)
			raise web.seeother("/manage_services.html")
		else:
			append_user_alerts("error",'ERROR',"Service is not deployed on that environment." + str(c.rowcount))
			raise web.seeother("/manage_services.html")

class deploy_service:
	def POST(self):

		input = web.input( sid="NULL", eid=["NULL"] )
		if input.sid == "NULL" or len(input.eid) == 0 or input.eid[0] == "NULL":
			raise web.badRequest()

		conn = sqlite3.connect('./data/site.db')
		c = conn.cursor()

		for i in input.eid:
			c.execute("SELECT * FROM service_deployment_lkp WHERE eid = ? AND sid = ?",(i,input.sid,))
			if c.rowcount > 0:
				raise web.badrequest()

		c.execute("SELECT * FROM services WHERE sid = ?",(input.sid,))
		service_info = c.fetchone()
		for env in input.eid:
			c.execute("SELECT * FROM servers WHERE eid = ?",(env,))
			servers = c.fetchall()
			for server in servers:
				analytics_server = AnalyticsServer( server )
				response = analytics_server.new( doc_root, service_info )
				append_user_alerts( 'info', 'Server response' , "deploying the service was a " + response )

		for i in input.eid:
			c.execute("INSERT INTO service_deployment_lkp VALUES (?,?)", (i,input.sid,))
		conn.commit()
		conn.close()

		msg = ''
		for i in input.eid:
			msg += ', ' + i 

		append_user_alerts('success', 'Success', 'Service sucessfully deployed  in ' + msg)
		raise web.seeother("/manage_services.html")

class server_status:
	def POST(self):
		input = web.input()
		conn = sqlite3.connect('./data/site.db', isolation_level=None)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		c.execute("SELECT * FROM servers WHERE srv_id = ?",(input.srv_id,))
		analytics_server = AnalyticsServer( c.fetchone() )
		print analytics_server.status()

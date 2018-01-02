import web
import HelperFunctions as help
from AnalyticsServerInterface import Server
from DatabaseHandler import DatabaseHandler as db

render = web.template.render('templates')


class Manage_Servers:
	def GET(self):
		# Extract Server Information and send it to the page.
		help.check_access()

		servers = db().executeLiteral( "SELECT srv_id, eid, display_name, machine_address, a_port_num, m_port_num FROM servers",[])

		serverInfo = []
		for each in servers:
			each = list( each )
			temp = [each[0]]
			if each[1] == 0:
				temp.append( "N/A" )
			else:
				temp.append( db().executeLiteral( "SELECT name FROM environments WHERE eid = ?", [each[1]] )[0][0] )
			temp += each[2:]
			serverInfo.append( temp )

		return help.renderPage( 'Manage Servers', render.manage_servers( serverInfo ) )

class AJAX_manage_servers:
	def GET(self, srv_id):
		# Message the server asking regarding its status
		help.check_access()
		usr = (web.ctx.session).username
		token = (web.ctx.session).access_token
		msgHeader = {"Username":usr, "Access-Token":token}

		serverInfo = db().executeLiteral( "SELECT machine_address, m_port_num FROM servers WHERE srv_id = ?" , [srv_id])[0]
		status = Server( serverInfo[0], serverInfo[1] ).send( "GET", "/STATUS/*", headers=msgHeader, timeout=5 )
		
		if status == "FAILED" or status[0] != "200":
			return '{"Management":"REJECTING", "Analytic":"REJECTING"}'
		else:
			return '{"Management":"ACCEPTING","Analytic":"' + status[1][-10:-1].upper() + '"}'



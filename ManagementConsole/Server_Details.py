import web
import HelperFunctions as help
import pylibconfig2 as cfg
from os.path import isfile, join

from logger import Logger
from DatabaseHandler import DatabaseHandler as db

render = web.template.render('templates')

class Server_Details:
	def GET(self, srv_id):
		help.check_access()

		# Get Server Information
		Server = list(db().executeLiteral( "SELECT * FROM servers WHERE srv_id = ?", [srv_id])[0])
		if Server[1] == 0:
			Server = ["N/A"] + Server
		else:
			name = db().executeLiteral( "SELECT name FROM environments WHERE eid = ?", [Server[1]])[0][0]
			Server = [name] + Server

		# Get Service information for the server
		Services = db().execute( "Server_Details", 1, [Server[1]])
		data = []
		for ser in Services:
			result = Logger().getAnalytics( srv_id, ser[0] )
			data.append( [ser[2], ser[1], result[2], result[3], result[4], str( result[0] ) + '-' + str( result[1] )] )

		path = join("./configs/", srv_id)
		file_reader = open( path, "r")
		master = cfg.Config( file_reader.read() )
		file_reader.close()

		masterInfo = [['Analytics Server' , master.Analytic_Settings.items()]
					, ['Management Server', master.Management_Settings.items()]
					, ['Data Logger', master.Logging.items()]]

		return help.renderPage("Server Details", render.server_details( Server, data, masterInfo ))
import web
from DatabaseHandler import DatabaseHandler as db
import HelperFunctions as help

render = web.template.render('templates')

class Manage_Paths:
	def GET( self ):
		# Get all paths from database
		all_paths = db().execute( "Path_Manage", 0, [])
		path_info = []
		types = ['DEV','TEST','STAGING','LIVE']

		# Sort the according to the types hierachy
		for path in all_paths:
			temp = [path[0], path[2], path[1]]
			for t in types:
				temp.append( (db().execute( "Path_Manage", 1, [path[0], t])[0])[0] )
			path_info.append( temp )
		return help.renderPage( "Environment Paths", render.paths( path_info ) )
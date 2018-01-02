import web
from DatabaseHandler import DatabaseHandler as db
import HelperFunctions as help

render = web.template.render('templates')

class Add_Path:
	def GET( self ):
		help.check_access()
		redirect()
		return help.renderPage( "Add Path", render.path_forms( 0, [] ) )

	def POST( self ):
		help.check_access()
		redirect()

		input = web.input( name="NULL" )
		if input.name == "NULL":
			help.append_user_alerts( "warning", "Invalid Entry", "The Path Name was invalid, please try again")
			return help.renderPage( "Add Path", render.path_forms( 0, [input.name, input.desc] ) )

		pid = db().executeID( "Path_Forms", 0, [input.name, input.desc] )
		raise web.seeother("path_details_" + str(pid))

class Edit_Path:
	def GET( self, pid ):
		help.check_access()
		redirect()
		path_info = db().execute( "Path_Forms", 1, [pid] )[0]
		return help.renderPage( "Add Path", render.path_forms( path_info[0], [path_info[2], path_info[3]] ) )

	def POST( self, pid ):
		help.check_access()
		redirect()

		input = web.input( name="NULL" )
		if input.name == "NULL":
			help.append_user_alerts( "warning", "Invalid Entry", "The Path Name was invalid, please try again")
			return help.renderPage( "Add Path", render.path_forms( 0, [input.name, input.desc] ) )

		db().execute( "Path_Forms", 2, [input.name, input.desc, pid])

		raise web.seeother("path_details_" + str(pid))

class Delete_Path:
	def GET( self, pid ):
		help.check_access()

		# Count Services currently on path
		count = db().executeLiteral( "SELECT count(*) FROM services WHERE pid = ?", [pid] )[0][0]
		if( count != 0):
			help.append_user_alerts( "warning", "Development Path still followed!", "You cannot delete a path when services are still following it, please redirect them before trying again." )
			return web.seeother( "path_details_" + str(pid) )

		db().executeLiteral( "DELETE FROM paths WHERE pid = ?", [pid] )
		db().executeLiteral( "DELETE FROM env_path_lkp WHERE pid = ?", [pid])

		help.append_user_alerts( "info", "Path Deleted", "Information about the path has been deleted.")
		raise web.seeother( "paths.html" )

def redirect():
	count = db().executeLiteral( "SELECT count(*) FROM environments", [])[0][0]
	if(count == 0):
		help.append_user_alerts('info', 'Need Environments first!', 'You cannot create a new path without having Environments to traverse, please create an Environment now.')
		raise web.seeother( "environment_form_0")